from rest_framework import routers
from django.conf.urls import include, url
from django.urls import path
from .views import UserViewset, registration_view, userView, searchUserView

router = routers.DefaultRouter()

router.register('users', UserViewset)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', registration_view),
    path('user/me/', userView.as_view()),
    url('users/search/$', searchUserView.as_view()),
]
