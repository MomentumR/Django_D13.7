import datetime
import pytz
from random import choice

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache

from env import TZ
from .filters import CommentFilter
from .models import Post, OneTimeCode, Comment
from .forms import VerifyEmailForm, PostForm, CommentForm,NewsForm
from .tasks import resend_verification_code
from .utils import codes, menu, send_news_to_subscribers


class AdsListView(ListView):
    """Main page view, list of posts """

    template_name = 'pcf/postList.html'
    queryset = Post.objects.order_by('-created_at').annotate(comments_count=Count('comments')).select_related('author')
    context_object_name = 'posts'
    extra_context = {'menu': menu}
    paginate_by = 10

    def get_queryset(self):
        queryset = cache.get('post_list', None)

        if not queryset:
            queryset = Post.objects.order_by('-created_at').annotate(comments_count=Count('comments')).select_related('author')
            cache.set('post_list', queryset)

        return queryset


class AdDetailView(DetailView):
    """Post detail view with its content and comments"""

    model = Post
    template_name = 'pcf/postDetails.html'
    context_object_name = 'post'
    extra_context = {'menu': menu}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = post.comments.all().select_related('author')
        context['comments'] = comments
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    """Post create view"""

    form_class = PostForm
    template_name = 'pcf/postAdd.html'
    extra_context = {'menu': menu}
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = self.request.user
        form.instance.author = user
        response = super().form_valid(form)

        return response


class AdUpdateView(LoginRequiredMixin, UpdateView):
    """Updates existing post (only for its author)"""

    model = Post
    template_name = 'pcf/postAdd.html'
    form_class = PostForm
    extra_context = {'menu': menu}

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            raise PermissionDenied('Только автор объявления может его редактировать.')
        return super().dispatch(request, *args, **kwargs)


class PersonalPageView(LoginRequiredMixin, ListView):
    """Personal page for registered and verified users
    with all the comments from all users posts"""

    model = Comment
    template_name = 'pcf/personalPage.html'
    context_object_name = 'comments'
    extra_context = {'menu': menu}

    def get_queryset(self):
        queryset = Comment.objects.filter(post__author=self.request.user).order_by('-created_at').select_related('author')
        self.comment_filter = CommentFilter(self.request.GET or None, user=self.request.user, queryset=queryset)
        return self.comment_filter.qs


class VerifyEmailView(FormView):
    """Email Verification with OTC created on user signup.
    If user doesn't verify email within 24 hours - users
    account will be deleted."""

    template_name = 'pcf/verifyEmail.html'
    form_class = VerifyEmailForm
    success_url = reverse_lazy('home')
    extra_context = {'menu': [{'title': 'Выход', 'url_name': 'account_logout'}]}

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='verified_users').exists() or not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        code_object = OneTimeCode.objects.get(user=user)
        if code_object.code == form.instance.code:
            user.groups.add(Group.objects.get(name='verified_users'))
            code_object.delete()
            return super().form_valid(form)
        else:
            form.add_error(None, 'Неправильный код')
            return super().form_invalid(form)


class NewsCreationView(FormView):
    """Creates emails for subscribed users.
    Available for staff only"""

    template_name = 'pcf/news.html'
    form_class = NewsForm
    extra_context = {'menu': menu}
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied('Только админы могут рассылать новости')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        send_news_to_subscribers(form.cleaned_data['subject'], form.cleaned_data['content'])
        return super().form_valid(form)


@login_required
def email_resend(request, *args, **kwargs):
    """Resending email for verification with OTC with
     deleting previous one"""

    user = request.user
    timezone = pytz.timezone(TZ)
    time_left = str(user.date_joined + datetime.timedelta(days=1) - datetime.datetime.now(timezone)).split('.')[0]
    OneTimeCode.objects.get(user=user).delete()
    code = OneTimeCode.objects.create(user=user, code=choice(codes))
    resend_verification_code.apply_async(args=[code.code, user.email, time_left])
    return redirect('verify_email')


@login_required
def add_comment(request, pk):
    """Add comment to posts"""

    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', pk)


@login_required
def unsubscribe(request):
    """Email notifications unsubscribe"""

    if request.user.groups.filter(name='subscribed_users').exists():
        group = Group.objects.get(name='subscribed_users')
        group.user_set.remove(request.user)
        return render(request, 'pcf/message.html', context={'title': 'Отписка',
                                                            'message': 'Вы отписались от новостной рассылки.',
                                                            'menu': menu})
    else:
        return redirect('home')


@login_required
def subscribe(request):
    """Subscription to email notifications"""

    if not request.user.groups.filter(name='subscribed_users').exists():
        group = Group.objects.get(name='subscribed_users')
        group.user_set.add(request.user)
        return render(request, 'pcf/message.html', context={'title': 'Подписка',
                                                            'message': 'Вы подписались на новостную рассылку.',
                                                            'menu': menu})
    else:
        return redirect('home')


@login_required
def accept_comment(request, pk):
    """Comment acception by post author"""

    comment = Comment.objects.get(pk=pk)
    if comment.post.author != request.user:
        raise PermissionDenied('Принять отклик может только автор объявления, '
                               'под которым он было написан.')
    if not comment.accepted:
        comment.accepted = True
        comment.save()
    return JsonResponse({'accepted': True})


@login_required
def delete_comment(request, pk):
    """Comment deletion by post author"""

    comment = Comment.objects.get(pk=pk)
    if comment.post.author != request.user:
        raise PermissionDenied('Удалить отклик может только автор объявления, '
                               'под которым он было написан.')
    comment.delete()
    return JsonResponse({'deleted': True})


def permission_denied_view(request, exception=None):
    """403 handler"""

    context = {'message': str(exception), 'menu': menu}
    return render(request, '403.html', context=context, status=403)


def page_not_found_view(request, exception=None):
    """404 handler"""

    context = {'message': str(exception), 'menu': menu}
    return render(request, '404.html', context=context, status=404)


