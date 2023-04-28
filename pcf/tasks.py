from datetime import timedelta

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from env import EMAIL
from pcf.models import Post


@shared_task
def send_verification_code(code, email):
    send_mail(
        'Код для завершения регистрации на сайте PeaceCraftFun',
        f'Для завершения регистрации введите следующий код в '
        f'соответствующее поле на странице http://127.0.0.1:8000/verify_email:\n\n{code}\n\nНа это у вас есть 24 часа,'
        f' иначе ваш аккаунт будет удален.',
        EMAIL,
        [email],
        fail_silently=False
    )
    return 'Письмо с кодом отправлено'


@shared_task
def resend_verification_code(code, email, time_left):
    send_mail(
        'Повторная отправка кода подтверждения email с сайта PeaceCraftFun',
        f'Для завершения регистрации введите следующий код в '
        f'соответствующее поле на странице http://127.0.0.1:8000/verify_email:\n\n{code}\n\n'
        f'У вас осталось {time_left}. Предыдущие коды не действуют.',
        EMAIL,
        [email],
        fail_silently=False
    )
    return 'Повторная отпавка письма с кодом'


@shared_task
def check_user_verified(user_id):
    try:
        user = User.objects.get(id=user_id)
        if not user.groups.filter(name='verified_users').exists():
            user.delete()
            return f'Юзер {user.username} удален'
    except User.DoesNotExist:
        return 'Юзер уже удален'
    return f'{user.username} подтвердил регистрацию'


@shared_task
def notify_post_author(email, post_title, comment_author, comment_text):
    send_mail(
        f'Новый отклик на ваше объявление {post_title} на сайте PeaceCraftFun',
        f'Пользователь {comment_author} оставил следующий отклик под вашим объявлением:\n\n'
        f'{comment_text}',
        EMAIL,
        [email],
        fail_silently=False
    )

    return f'Уведомление о новом отклике отправлено на {email}'


@shared_task
def notify_subscribers_weekly():
    subscribers_emails = User.objects.filter(groups__name='subscribed_users').values_list('email', flat=True)
    new_posts = '<br>'.join(f'<a href="http://127.0.0.1:8000/{post[1]}">{post[0]}</a>'
                            for post in Post.objects.filter(created_at__gte=(timezone.now()-timedelta(days=7)))
                            .values_list('title', 'pk'))
    send_mail(
        subject='[PeaceCraftFun] Список новых объявлений за неделю!',
        message='',
        html_message=new_posts + f'<hr><br><p>Если вы хотите отписаться от рассылки '
                                 f'- зайдите в свой аккаунт и перейдите по '
                                 f'<a href="http://127.0.0.1:8000/unsubscribe">этой ссылке</a>.</p>',
        recipient_list=subscribers_emails,
        from_email=EMAIL,
        fail_silently=False
    )


@shared_task
def notify_comment_author(post_title, email, comment_text):
    send_mail(
        subject=f'[PeaceCraftFun] Ваш отклик принят!',
        message=f'Ваш отклик\n\n{comment_text}\n\n на объявление\n\n{post_title}\n\n принят!',
        recipient_list=[email],
        from_email=EMAIL
    )
    return f'Уведомление о принятом отклике отправлено на {email}'


