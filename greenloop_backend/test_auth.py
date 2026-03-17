import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenloop_backend.settings')
django.setup()

from django.contrib.auth import authenticate
from users.models import User

user = authenticate(email='admin@gmail.com', password='admin')
print("Authenticate 'admin' password:", user)

user = authenticate(email='admin@gmail.com', password='admin135')
print("Authenticate 'admin135' password:", user)

u = User.objects.get(email='admin@gmail.com')
print("User hash:", u.password)
print("Check password 'admin135':", u.check_password('admin135'))
print("User is_staff:", u.is_staff)
print("User is_active:", u.is_active)
print("User check:", authenticate(username='admin@gmail.com', password='admin135'))

