from django.urls import path
from .views import register, login
from .views import register, login, all_users

urlpatterns = [

path('register/', register),
path('login/', login),
path('users/', all_users),

]