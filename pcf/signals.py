from random import choice

from allauth.account.signals import user_signed_up
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OneTimeCode, Comment
from .tasks import send_verification_code, check_user_verified, notify_post_author, notify_comment_author
from .utils import codes


@receiver(user_signed_up)
def create_code(sender, request, user, **kwargs):
    code = OneTimeCode.objects.create(user=user, code=choice(codes))
    send_verification_code.apply_async(args=[code.code, user.email])
    check_user_verified.apply_async(args=[user.id], countdown=86400)


@receiver(post_save, sender=Comment)
def notify_author(sender, instance, created, **kwargs):
    post = instance.post
    post_author_email = post.author.email
    post_title = post.title
    if created:
        notify_post_author.apply_async(args=[post_author_email, post_title, str(instance.author), instance.text])
    else:
        notify_comment_author.apply_async(args=[post_title, str(instance.author.email), instance.text])

