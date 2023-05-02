from django.urls import path
from .views import *


urlpatterns = [
    path('v1/posts_list/', PostAPIView.as_view(), name='posts_list')
]