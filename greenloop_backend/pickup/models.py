from django.contrib.gis.db import models
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import hashlib


class PickupSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.date} ({self.start_time} - {self.end_time})"

    class Meta:
        verbose_name = "Pickup Slot"
        verbose_name_plural = "Pickup Slots"


class Pickup(models.Model):

    # Item type: the specific type of waste item being collected
    CATEGORY = (
        ('ampoules', 'Ampoules'),
        ('vials', 'Medicine Vials'),
        ('blades', 'Blades'),
        ('needles', 'Needles'),
        ('scalpels', 'Scalpels'),
        ('catheters', 'Catheters'),
        ('gloves', 'Gloves'),
        ('intravenous_tubes', 'Intravenous Tubes'),
        ('tubing', 'Tubing'),
        ('urine_bags', 'Urine Bags'),
        ('kids_diaper', 'Kids Diaper'),
        ('adult_diaper', 'Adult Diaper'),
        ('sanitary_pad', 'Sanitary Pad'),
        ('medical_waste', 'Medical Waste'),
        ('discreet', 'Discreet Waste'),
        ('hair', 'Hair'),
    )

    STATUS = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    # Waste category: broad classification (dry/wet/e-waste/biomedical)
    WASTE_TYPES = [
        ('dry', 'Dry'),
        ('wet', 'Wet'),
        ('e-waste', 'E-Waste'),
        ('biomedical', 'Biomedical')
    ]

    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=50, choices=CATEGORY)
    address = models.TextField()

    scheduled_date = models.DateField()
    location = models.PointField(null=True, blank=True)
    qr_code = models.CharField(max_length=64, unique=True, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    ward = models.ForeignKey('users.Ward', on_delete=models.SET_NULL, null=True, blank=True)
    slot = models.ForeignKey(PickupSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='pickups')

    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pickups')

    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fee_paid = models.BooleanField(default=False)
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPES, default='dry')
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['ward', 'scheduled_date', 'status']),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Pickup.objects.filter(pk=self.pk).first()
            # Set completed_at when transitioning to 'completed' from any active status
            if (old_instance
                    and old_instance.status in ('pending', 'assigned')
                    and self.status == 'completed'
                    and not self.completed_at):
                self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item


@receiver(post_save, sender=Pickup)
def generate_qr_code(sender, instance, created, **kwargs):
    """Auto-generate a unique SHA-256 QR code hash on pickup creation."""
    if created and not instance.qr_code:
        ward_id = str(instance.ward.id) if instance.ward else ""
        raw_string = f"{instance.id}{instance.resident.id}{ward_id}{instance.created_at.timestamp()}"
        instance.qr_code = hashlib.sha256(raw_string.encode()).hexdigest()
        instance.save(update_fields=['qr_code'])


class Route(models.Model):
    hks_worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    ward = models.ForeignKey('users.Ward', on_delete=models.CASCADE)
    route_date = models.DateField()
    planned_path = models.LineStringField(null=True, blank=True)
    actual_path = models.LineStringField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['hks_worker', 'route_date']),
        ]

    def __str__(self):
        return f"Route for {self.hks_worker.username} on {self.route_date}"