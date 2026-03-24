import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenloop_backend.settings")
django.setup()

from rest_framework.test import APIClient
from users.models import User, Ward
from pickup.models import PickupSlot

def test_endpoints():
    client = APIClient()
    
    User.objects.filter(email='testres@example.com').delete()
    User.objects.filter(email='admin_test@test.com').delete()
    User.objects.filter(email='testwork@example.com').delete()
    Ward.objects.filter(name='Test Ward').delete()
    
    ward = Ward.objects.create(name='Test Ward', boundary='POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))')
    
    print("--- User Authentication & Roles ---")
    resp = client.post('/api/auth/register/', {'username': 'testres', 'email': 'testres@example.com', 'password': 'pass', 'phone': '1234567890', 'ward': 'Test Ward', 'role': 'resident'})
    print(f"Register Resident: {resp.status_code}")
    
    resp = client.post('/api/auth/login/', {'email': 'testres@example.com', 'password': 'pass'})
    print(f"Login Resident: {resp.status_code}")
    res_token = resp.data['tokens']['access']

    print("\n--- Resident Endpoints ---")
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + res_token)
    
    slot, _ = PickupSlot.objects.get_or_create(date='2030-01-01', start_time='10:00:00', end_time='12:00:00')
    location_data = 'SRID=4326;POINT(75.0 11.0)'
    
    resp = client.post('/api/pickups/', {
        'item': 'hair', 'address': '123 Test', 'scheduled_date': '2030-01-01', 
        'slot': slot.id, 'waste_type': 'dry', 'location': location_data, 'ward': ward.id
    }, format='json')
    print(f"Create Pickup with Location: {resp.status_code}")
    if resp.status_code != 201:
        print("  Error:", resp.data)
    
    resp = client.get('/api/auth/profile/')
    print(f"Get Profile: {resp.status_code}")
    
    print("\n--- Admin Endpoints ---")
    admin_user, _ = User.objects.get_or_create(username='admin_test', email='admin_test@test.com', defaults={'role': 'admin'})
    admin_user.set_password('pass')
    admin_user.save()
    
    resp = client.post('/api/auth/login/', {'email': 'admin_test@test.com', 'password': 'pass'})
    admin_token = resp.data['tokens']['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + admin_token)
    
    resp = client.post('/api/auth/create-hks-worker/', {'username': 'testwork', 'email': 'testwork@example.com', 'password': 'pass', 'phone': '9876543210', 'ward': 'Test Ward'})
    print(f"Create HKS Worker: {resp.status_code}")
    
    resp = client.get('/api/auth/dashboard/')
    print(f"Admin Dashboard Main: {resp.status_code}")
    
    print("\n--- Location & Tracking Endpoints ---")
    resp = client.get('/api/auth/dashboard/live-map/')
    print(f"Live Map Load (Admin): {resp.status_code}")
    
    resp = client.post('/api/auth/login/', {'email': 'testwork@example.com', 'password': 'pass'})
    work_token = resp.data['tokens']['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + work_token)
    
    resp = client.post('/api/auth/update-location/', {'latitude': '12.970', 'longitude': '77.590'})
    print(f"Update Location (HKS Worker): {resp.status_code}")
    if resp.status_code != 200:
        print("  Error:", resp.data)
        
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + admin_token)
    resp = client.get('/api/auth/dashboard/live-map/')
    print(f"Live Map Data (Admin) after location update: {resp.status_code}")
    workers = resp.data.get('workers', [])
    if workers:
        print(f"  => SUCCESS! Tracking data visible: {workers[0]['username']} at [{workers[0]['latitude']}, {workers[0]['longitude']}]")
    else:
        print("  => FAILED: Worker location not shown in live map.")

test_endpoints()
