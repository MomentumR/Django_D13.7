from django import template


register = template.Library()


@register.filter(name='is_subscribed')
def is_subscribed(user):
    return user.groups.filter(name='subscribed_users').exists()
