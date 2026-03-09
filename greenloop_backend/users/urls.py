from django.urls import path
from .views import register, login, forgot_password, reset_password, all_users, admin_dashboard, my_profile
from .views import admin_dashboard


urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('users/', all_users),
    path('dashboard/', admin_dashboard),
    path('forgot-password/', forgot_password),
    path('reset-password/<int:uid>/<str:token>/', reset_password),
    path('profile/', my_profile),
]
