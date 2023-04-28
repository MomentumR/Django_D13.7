from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextFormField

from .models import Post, OneTimeCode, Comment


class CustomSignupForm(SignupForm):
    subscribe = forms.BooleanField(label='Подписаться на новостную рассылку',
                                   required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                              'type': 'checkbox'}))

    field_order = ['username', 'email', 'password1', 'password2', 'subscribe']

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        if self.cleaned_data['subscribe']:
            subscribed_group = Group.objects.get(name='subscribed_users')
            subscribed_group.user_set.add(user)

        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'content']
        labels = {
            'category': 'Выберите категорию',
            'title': '',
            'content': ''
        }

        widgets = {
            'content': CKEditorWidget(),
            'category': forms.Select(attrs={'class': 'form-select form-select-sm mx-auto my-3',
                                            'style': 'max-width:200px'}),
            'title': forms.TextInput(attrs={'class': 'form-control mx-auto my-4',
                                            'style': 'max-width:500px',
                                            'placeholder': 'Введите заголовок...'})
        }


class VerifyEmailForm(forms.ModelForm):
    class Meta:
        model = OneTimeCode
        fields = ['code']
        labels = {'code': 'Введите код из письма'}

        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class NewsForm(forms.Form):
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mx-auto',
                                                                            'placeholder': 'Введите тему письма',
                                                                            'style': 'max-width:500px'}))
    content = RichTextFormField()

