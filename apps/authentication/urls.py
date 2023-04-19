# -*- encoding: utf-8 -*-

from django.urls import path, include
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from allauth.account.views import LoginView, SignupView 

urlpatterns = [
    path('login/', login_view, name="make_account"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="signout"),
]
