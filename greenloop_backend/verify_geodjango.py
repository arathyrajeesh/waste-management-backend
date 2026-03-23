import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenloop_backend.settings')
django.setup()

from django.contrib.gis.geos import Point
from pickup.models import SpatialTest
from django.db import connection

def verify_spatial():
    print("Checking PostGIS version...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT PostGIS_Version();")
        version = cursor.fetchone()
        print(f"PostGIS Version: {version[0]}")

    print("\nCreating test spatial record...")
    p1 = Point(12.9716, 77.5946) # Bangalore
    test_obj = SpatialTest.objects.create(name="Test Point", location=p1)
    print(f"Created: {test_obj.name} at {test_obj.location}")

    print("\nRunning spatial query (ST_Within)...")
    # Buffer around Bangalore
    from django.contrib.gis.measure import D
    results = SpatialTest.objects.filter(location__distance_lte=(p1, D(m=100)))
    if results.exists():
        print(f"Success! Found {results.count()} point(s) within 100m.")
    else:
        print("Failure: Point not found in distance query.")

    # Cleanup
    test_obj.delete()
    print("\nTest completed.")

if __name__ == "__main__":
    verify_spatial()
