from django.urls import path
from .views import register, login, forgot_password,reset_password

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('forgot-password/', forgot_password),
    path('reset-password/<int:uid>/<str:token>/', reset_password),
]