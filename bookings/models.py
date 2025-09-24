from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

User = settings.AUTH_USER_MODEL

class Slot(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_time']
        unique_together = ('provider', 'start_time')

    def __str__(self):
        return f"{self.provider} {self.start_time:%Y-%m-%d %H:%M}" 

class Appointment(models.Model):
    APPOINTMENT_TYPES = (
        ('consultation', 'General Consultation'),
        ('followup', 'Follow-up Visit'),
        ('checkup', 'Routine Check-up'),
        ('emergency', 'Emergency Consultation'),
        ('specialist', 'Specialist Consultation'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    slot = models.OneToOneField(Slot, on_delete=models.CASCADE, related_name='appointment')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='consultation')
    patient_notes = models.TextField(blank=True, help_text="Please describe your symptoms or reason for visit")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer} -> {self.slot} ({self.status})"


class Availability(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    interval_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('provider', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.provider} {self.date} {self.start_time}-{self.end_time}"

    def generate_slots(self):
        base_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        created = 0
        while base_dt < end_dt:
            next_dt = base_dt + timedelta(minutes=self.interval_minutes)
            if next_dt > end_dt:
                break
            Slot.objects.get_or_create(
                provider=self.provider,
                start_time=base_dt,
                end_time=next_dt,
                defaults={'is_booked': False}
            )
            base_dt = next_dt
            created += 1
        return created
