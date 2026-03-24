import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenloop_backend.settings")
django.setup()

from users.models import Ward
from django.contrib.gis.geos import Point

wards = Ward.objects.all()
print(f"Total wards loaded: {wards.count()}")

# Coordinate inside Pilot Ward 1: (77.595, 12.975)
p = Point(77.595, 12.975, srid=4326)
wards_containing = Ward.objects.filter(boundary__contains=p)
print(f"Wards containing point {p}: {wards_containing.count()}")
for w in wards_containing:
    print(f" - {w.name}")

explain_output = wards_containing.explain()
print("\n--- EXPLAIN OUTPUT ---")
print(explain_output)
