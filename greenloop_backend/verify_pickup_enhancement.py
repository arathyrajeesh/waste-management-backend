import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenloop_backend.settings")
django.setup()

from pickup.models import Pickup
from users.models import User, Ward
from django.contrib.gis.geos import Point
from django.utils import timezone
import datetime

ward, _ = Ward.objects.get_or_create(name='Test Ward Pickup', defaults={'boundary': 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'})
resident, _ = User.objects.get_or_create(username='rpickup', email='rpickup@test.com', defaults={'role': 'resident'})

# Force reset of DB states just in case
Pickup.objects.filter(resident=resident).delete()

p = Pickup.objects.create(
    resident=resident,
    ward=ward,
    item='medical_waste',
    address='123 Test St',
    scheduled_date=datetime.date.today(),
    waste_type='dry',
    location=Point(75.78, 11.25, srid=4326),
    status='pending'
)

if p.location and p.location.x == 75.78 and p.location.y == 11.25:
    print("SUCCESS: location saved with valid spatial geometry")
else:
    print("FAILED: geometry mismatch")

if p.qr_code and len(p.qr_code) == 64:
    print(f"SUCCESS: SHA-256 qr_code hash generated: {p.qr_code}")
else:
    print(f"FAILED: qr_code missing or invalid length: {p.qr_code}")

p.status = 'completed'
p.save()

p.refresh_from_db()
if p.completed_at and (timezone.now() - p.completed_at).total_seconds() < 10:
    print(f"SUCCESS: completed_at automatically set to {p.completed_at}")
else:
    print(f"FAILED: completed_at not set or incorrect")

index_found = any(list(idx.fields) == ['ward', 'scheduled_date', 'status'] for idx in Pickup._meta.indexes)
if index_found:
    print("SUCCESS: Composite index found on (ward, scheduled_date, status)")
else:
    print("FAILED: Composite index not found")
