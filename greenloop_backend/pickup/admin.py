from django.contrib import admin
from .models import Pickup, PickupSlot

@admin.register(PickupSlot)
class PickupSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time')
    list_filter = ('date',)

@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ('item', 'resident', 'date', 'slot', 'status', 'fee_paid')
    list_filter = ('status', 'waste_type', 'date', 'slot')
    search_fields = ('item', 'resident__username', 'address')