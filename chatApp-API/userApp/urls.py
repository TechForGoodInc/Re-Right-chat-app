from rest_framework import routers
from django.conf.urls import url
from django.urls import path,include
from .views import UserViewset, registration_view, userView, searchUserView

router = routers.DefaultRouter()

router.register('users', UserViewset)

urlpatterns = [
    url('users/search/$', searchUserView.as_view(), name='search_user'),
    path('', include(router.urls)),
    path('register/', registration_view),
    path('user/me/', userView.as_view()),
]
