import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenloop_backend.settings")
django.setup()

from pickup.models import Route
from users.models import User, Ward
from django.contrib.gis.geos import LineString
from django.db.models import Func, FloatField
import datetime

ward, _ = Ward.objects.get_or_create(name='Route Ward', defaults={'boundary': 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'})
worker, _ = User.objects.get_or_create(username='worker1', email='w1@test.com', defaults={'role': 'hks_worker'})

Route.objects.filter(hks_worker=worker).delete()

planned_coords = [(float(i), float(i)) for i in range(20)]
planned_path = LineString(planned_coords)

actual_coords = [(float(i), float(i) + 0.1) for i in range(20)]
actual_path = LineString(actual_coords)

route = Route.objects.create(
    hks_worker=worker,
    ward=ward,
    route_date=datetime.date.today(),
    planned_path=planned_path,
    actual_path=actual_path
)

if route.planned_path.num_coords == 20:
    print("SUCCESS: planned_path saved with 20 coordinate pairs in PostGIS")
else:
    print("FAILED: geometry mismatch in planned_path")

deviation_query = Route.objects.filter(id=route.id).annotate(
    deviation=Func(
        'planned_path', 'actual_path',
        function='ST_HausdorffDistance',
        output_field=FloatField()
    )
).first()

if deviation_query and deviation_query.deviation is not None:
    print(f"SUCCESS: HausdorffDistance returned a deviation metric: {deviation_query.deviation}")
else:
    print("FAILED: Failed to calculate HausdorffDistance")

index_found = any(list(idx.fields) == ['hks_worker', 'route_date'] for idx in Route._meta.indexes)
if index_found:
    print("SUCCESS: Composite index found on (hks_worker, route_date)")
else:
    print("FAILED: Composite index not found")
