from django.contrib.gis.db import models
from users.models import User

class SpatialTest(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        return self.name

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

    CATEGORY = (
        ('ampoules','Ampoules'),
        ('vials','Medicine Vials'),
        ('blades','Blades'),
        ('needles','Needles'),
        ('scalpels','Scalpels'),
        ('catheters','Catheters'),
        ('gloves','Gloves'),
        ('intravenous_tubes','Intravenous Tubes'),
        ('tubing','Tubing'),
        ('urine_bags','Urine Bags'),
        ('kids_diaper','Kids Diaper'),
        ('adult_diaper','Adult Diaper'),
        ('sanitary_pad','Sanitary Pad'),
        ('medical_waste','Medical Waste'),
        ('discreet','Discreet Waste'),
        ('hair','Hair'),
    )

    STATUS = (
        ('pending','Pending'),
        ('collected','Collected'),
    )

    resident = models.ForeignKey(User, on_delete=models.CASCADE)

    item = models.CharField(
        max_length=50,
        choices=CATEGORY
    )

    address = models.TextField()

    date = models.DateField()
    
    # New slot field
    slot = models.ForeignKey(PickupSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='pickups')

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pickups')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fee_paid = models.BooleanField(default=False)
    
    WASTE_TYPES = [
        ('dry', 'Dry'), 
        ('wet', 'Wet'), 
        ('e-waste', 'E-Waste'), 
        ('biomedical', 'Biomedical')
    ]
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPES, default='dry')
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item