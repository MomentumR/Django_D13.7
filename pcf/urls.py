from django.urls import path

from pcf.views import *

urlpatterns = [
    path('', AdsListView.as_view(), name='home'),
    path('<int:pk>/', AdDetailView.as_view(), name='post'),
    path('verify_email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend_code/', email_resend, name='resend_code'),
    path('post_add/', AdCreateView.as_view(), name='post_add'),
    path('<int:pk>/add_comment/', add_comment, name='add_comment'),
    path('<int:pk>/post_update/', AdUpdateView.as_view(), name='post_update'),
    path('news/', NewsCreationView.as_view(), name='news'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
    path('subscribe/', subscribe, name='subscribe'),
    path('personal_page/', PersonalPageView.as_view(), name='personal_page'),
    path('<int:pk>/accept_comment/', accept_comment, name='accept_comment'),
]
