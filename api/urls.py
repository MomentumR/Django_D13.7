from django.urls import path, include
from requests import delete

from .views import *
from .routers import post_router

app_name = 'api'

urlpatterns = [
    # path('v1/post_list/', PostListAPIView.as_view()),
    # path('v1/post/<int:pk>/', PostSingleView.as_view()),
    # path('v1/post/', PostViewSet.as_view({'get': 'list'})),
    # path('v1/post/<int:pk>', PostViewSet.as_view({'get': 'retrieve'})),
    # path('v1/post/', PostViewSet.as_view({'post': 'create'})),
    path('v1/', include(post_router.urls)),
    path('v1/subscribe/', subscribe),
    path('v1/unsubscribe/', unsubscribe),
    path('v1/personal_page/', PersonalPageView.as_view()),
    path('v1/post/<int:post_id>/add_comment/', CommentAddAPIView.as_view()),
]