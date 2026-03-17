import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenloop_backend.settings')
django.setup()

from django.contrib.auth import authenticate

user = authenticate(username='admin@gmail.com', password='admin135')
print("Authenticate custom backend:", user)
