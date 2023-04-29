from django.contrib.auth.models import User
from django.core.mail import send_mail

from env import EMAIL

codes = list(range(100000, 1000000))

menu = [{'title': 'Главная', 'url_name': 'home'},
        {'title': 'Добавить', 'url_name': 'post_add'},
        {'title': 'Рассылка', 'url_name': 'news'},
        {'title': 'Личка', 'url_name': 'personal_page'},
        {'title': 'Подписаться', 'url_name': 'subscribe'},
        {'title': 'Отписаться', 'url_name': 'unsubscribe'},
        {'title': 'Выход', 'url_name': 'account_logout'},
        {'title': 'Вход', 'url_name': 'account_login'},
        ]


def send_news_to_subscribers(subject, content):
    """Send news to subscribers created by site staff"""

    subscribers_emails = User.objects.filter(groups__name='subscribed_users').values_list('email', flat=True)
    send_mail(
        subject=f'[PeaceCraftFun] {subject}',
        message='',
        html_message=content + f'<hr><br><p>Если вы хотите отписаться от рассылки - '
                               f'зайдите в свой аккаунт и перейдите по '
                               f'<a href="http://127.0.0.1:8000/unsubscribe">этой ссылке</a>.</p>',
        recipient_list=subscribers_emails,
        from_email=EMAIL,
        fail_silently=False
    )

