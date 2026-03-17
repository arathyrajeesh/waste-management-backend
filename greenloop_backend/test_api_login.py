import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenloop_backend.settings')
django.setup()

from rest_framework.test import APIClient

client = APIClient()
res = client.post('/api/auth/login/', {'email': 'admin@gmail.com', 'password': 'admin135'})
print("Status:", res.status_code)
print("Data:", res.data)
