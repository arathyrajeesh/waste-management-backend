import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from users.models import Ward
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Seed Ward model from GeoJSON file'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, nargs='?', help='Path to GeoJSON file.', default='data/pilot_wards.geojson')

    def handle(self, *args, **kwargs):
        file_path = kwargs['geojson_file']
        
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
            
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        features = data.get('features', [])
        count = 0
        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            name = props.get('name', f"Ward {count+1}")
            
            ward, created = Ward.objects.update_or_create(
                name=name,
                defaults={'boundary': GEOSGeometry(json.dumps(geom))}
            )
            count += 1
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created ward: {name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated ward: {name}'))
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} wards'))
