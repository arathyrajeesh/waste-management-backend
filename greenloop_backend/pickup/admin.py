from django.contrib import admin
from .models import Pickup, PickupSlot
from users.models import User

@admin.register(PickupSlot)
class PickupSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time')
    list_filter = ('date',)

@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ('item', 'resident', 'date', 'slot', 'status', 'assigned_worker', 'fee_paid')
    list_filter = ('status', 'waste_type', 'date', 'slot', 'assigned_worker')
    search_fields = ('item', 'resident__username', 'address')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_worker":
            kwargs["queryset"] = User.objects.filter(role='hks_worker')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)