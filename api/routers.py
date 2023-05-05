from rest_framework import routers
from .views import PostViewSet

post_router = routers.SimpleRouter()

post_router.register(r'post', PostViewSet, basename='post')


