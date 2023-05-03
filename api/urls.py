from django.urls import path
from requests import delete

from .views import *

app_name = 'api'

urlpatterns = [
    path('v1/post_list/', PostListAPIView.as_view()),
    path('v1/post/<int:pk>/', PostSingleView.as_view()),
    path('v1/subscribe/', subscribe),
    path('v1/unsubscribe/', unsubscribe),
    path('v1/personal_page/', PersonalPageView.as_view()),
    path('v1/post/<int:post_id>/add_comment/', CommentAddAPIView.as_view()),
]