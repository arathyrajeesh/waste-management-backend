import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenloop_backend.settings')
django.setup()

client = Client()
# Get CSRF token
login_url = '/admin/login/'
response = client.get(login_url)
csrf_token = response.cookies['csrftoken'].value

# Attempt login
data = {
    'username': 'admin@gmail.com',
    'password': 'admin135',
    'csrfmiddlewaretoken': csrf_token,
}
response = client.post(login_url, data, follow=True)

if response.status_code == 200 and response.request['PATH_INFO'] == '/admin/':
    print("SUCCESS: Admin logged in with email.")
else:
    print("FAILURE: Admin could not log in with email.")
    print("Final URL:", response.request['PATH_INFO'])
    print("Status Code:", response.status_code)

