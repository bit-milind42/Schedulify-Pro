from django.contrib import admin
from .models import Slot, Appointment

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('provider', 'start_time', 'end_time', 'is_booked')
    list_filter = ('provider', 'is_booked')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('slot', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer__username', 'slot__provider__username')
