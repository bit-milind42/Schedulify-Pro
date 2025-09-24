from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Slot, Appointment, Availability
from accounts.models import User
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

@login_required
def slot_list(request):
    if not request.user.is_provider():
        return redirect('dashboard')
    slots = Slot.objects.filter(provider=request.user)
    return render(request, 'bookings/slot_list.html', {'slots': slots})

@login_required
def slot_create(request):
    if not request.user.is_provider():
        return redirect('dashboard')
    message = None
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        if start and end:
            from datetime import datetime
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                if end_dt > start_dt:
                    Slot.objects.create(provider=request.user, start_time=start_dt, end_time=end_dt)
                    return redirect('slot_list')
                else:
                    message = 'End must be after start'
            except ValueError:
                message = 'Invalid date format'
    return render(request, 'bookings/slot_create.html', {'message': message})

@login_required
def slot_delete(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id, provider=request.user, is_booked=False)
    slot.delete()
    return redirect('slot_list')

@login_required
def slot_edit(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id, provider=request.user, is_booked=False)
    message = None
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        from datetime import datetime
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            if end_dt > start_dt:
                slot.start_time = start_dt
                slot.end_time = end_dt
                slot.save()
                return redirect('slot_list')
            else:
                message = 'End must be after start'
        except ValueError:
            message = 'Invalid date format'
    return render(request, 'bookings/slot_edit.html', {'slot': slot, 'message': message})

@login_required
def appointment_list(request):
    mode = request.GET.get('mode')
    if request.user.is_provider() and mode == 'provider':
        appointments = Appointment.objects.filter(slot__provider=request.user)
    else:
        appointments = Appointment.objects.filter(customer=request.user)
    return render(request, 'bookings/appointment_list.html', {
        'appointments': appointments,
        'mode': mode,
        'now': timezone.now(),
    })

@login_required
@require_POST
def book_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id, is_booked=False)
    if request.user.is_provider():
        return redirect('providers_list')
    appt = Appointment.objects.create(slot=slot, customer=request.user)
    slot.is_booked = True
    slot.save()
    send_mail(
        'Appointment Request Submitted',
        f'Your appointment request with {slot.provider.username} at {slot.start_time} was submitted.',
        None,
        [request.user.email or 'test@example.com'],
        fail_silently=True,
    )
    if slot.provider.email:
        send_mail(
            'New Appointment Request',
            f'{request.user.username} requested {slot.start_time}.',
            None,
            [slot.provider.email],
            fail_silently=True,
        )
    return redirect('appointment_list')

@login_required
def provider_slots(request, provider_id):
    provider = get_object_or_404(User, id=provider_id, role='provider')
    # show only free slots
    slots = Slot.objects.filter(provider=provider, is_booked=False).order_by('start_time')
    return render(request, 'bookings/provider_slots.html', {'provider': provider, 'slots': slots})

@login_required
def appointment_action(request, appointment_id, action):
    appt = get_object_or_404(Appointment, id=appointment_id)

    def notify(subject, body, both=True):
        if appt.customer.email:
            send_mail(subject, body, None, [appt.customer.email], fail_silently=True)
        if both and appt.slot.provider.email:
            send_mail(subject, body, None, [appt.slot.provider.email], fail_silently=True)

    # Customer cancel
    if action == 'cancel' and appt.customer == request.user and appt.status in ('pending','approved'):
        appt.status = 'cancelled'
        appt.slot.is_booked = False
        appt.slot.save()
        appt.save()
        notify('Appointment Cancelled', f'Appointment on {appt.slot.start_time} cancelled by customer.')
        return redirect('appointment_list')

    if request.user.is_provider() and appt.slot.provider == request.user:
        # Approve / reject
        if appt.status == 'pending' and action in ('approve','reject'):
            if action == 'approve':
                appt.status = 'approved'
            else:
                appt.status = 'rejected'
                appt.slot.is_booked = False
                appt.slot.save()
            appt.save()
            notify('Appointment Status Updated', f'Appointment on {appt.slot.start_time} is now {appt.status}.')
            return redirect('appointment_list')
        # Complete after passed time
        if appt.status == 'approved' and action == 'complete' and appt.slot.start_time < timezone.now():
            appt.status = 'completed'
            appt.save()
            notify('Appointment Completed', f'Appointment on {appt.slot.start_time} marked completed.')
            return redirect('appointment_list')

    return redirect('appointment_list')

@login_required
def api_available_slots(request, provider_id):
    provider = get_object_or_404(User, id=provider_id, role='provider')
    date_filter = request.GET.get('date')
    qs = Slot.objects.filter(provider=provider, is_booked=False)
    
    if date_filter:
        from datetime import datetime, timedelta
        try:
            y, m, d = map(int, date_filter.split('-'))
            start_day = datetime(y, m, d)
            end_day = start_day + timedelta(days=1)
            qs = qs.filter(start_time__gte=start_day, start_time__lt=end_day)
        except ValueError:
            pass
    
    qs = qs.order_by('start_time')
    
    data = [{
        'id': s.id,
        'start': s.start_time.isoformat(),
        'end': s.end_time.isoformat(),
        'duration': int((s.end_time - s.start_time).total_seconds() / 60),
        'formatted_time': s.start_time.strftime('%I:%M %p'),
        'formatted_date': s.start_time.strftime('%B %d, %Y'),
    } for s in qs]
    
    return JsonResponse({
        'slots': data,
        'provider': {
            'name': f"Dr. {provider.first_name or provider.username}",
            'specialty': provider.specialty or 'General Practice'
        },
        'count': len(data)
    })

@login_required
def booking_wizard(request):
    # Step params via query: provider, date, slot
    provider_id = request.GET.get('provider')
    date = request.GET.get('date')
    slot_id = request.GET.get('slot')
    providers = User.objects.filter(role='provider')
    selected_provider = None
    available_slots = []
    
    if provider_id:
        selected_provider = User.objects.filter(id=provider_id, role='provider').first()
        if selected_provider:
            qs = Slot.objects.filter(provider=selected_provider, is_booked=False)
            if date:
                from datetime import datetime, timedelta
                try:
                    y,m,d = map(int, date.split('-'))
                    start_day = datetime(y,m,d)
                    end_day = start_day + timedelta(days=1)
                    qs = qs.filter(start_time__gte=start_day, start_time__lt=end_day)
                except ValueError:
                    pass
            available_slots = qs.order_by('start_time')
    
    confirm_slot = None
    if slot_id and request.method == 'POST':
        # final confirmation with enhanced data
        slot = get_object_or_404(Slot, id=slot_id, is_booked=False)
        if request.user.is_provider():
            return redirect('booking_wizard')
        
        appointment_type = request.POST.get('appointment_type', 'consultation')
        patient_notes = request.POST.get('patient_notes', '')
        
        appt = Appointment.objects.create(
            slot=slot, 
            customer=request.user,
            appointment_type=appointment_type,
            patient_notes=patient_notes
        )
        slot.is_booked = True
        slot.save()
        
        # Enhanced email notifications
        if request.user.email:
            send_mail(
                f'Appointment Request Submitted - {appointment_type.title()}',
                f'Your {appointment_type} appointment request for {slot.start_time.strftime("%B %d, %Y at %I:%M %p")} with Dr. {slot.provider.first_name or slot.provider.username} has been submitted successfully.\n\nAppointment Details:\n- Type: {appointment_type.title()}\n- Date & Time: {slot.start_time.strftime("%B %d, %Y at %I:%M %p")}\n- Duration: 30 minutes\n- Status: Pending approval\n\nYou will receive a confirmation email once your appointment is approved by the provider.',
                None,
                [request.user.email],
                fail_silently=True,
            )
        
        if slot.provider.email:
            send_mail(
                f'New Appointment Request - {appointment_type.title()}',
                f'You have received a new {appointment_type} appointment request.\n\nPatient: {request.user.first_name} {request.user.last_name} ({request.user.username})\nDate & Time: {slot.start_time.strftime("%B %d, %Y at %I:%M %p")}\nType: {appointment_type.title()}\nPatient Notes: {patient_notes or "None provided"}\n\nPlease log into your dashboard to approve or reject this request.',
                None,
                [slot.provider.email],
                fail_silently=True,
            )
        
        return redirect('booking_confirmation', appt.id)
    elif slot_id:
        confirm_slot = Slot.objects.filter(id=slot_id, is_booked=False).first()
    
    # Add context for today and max date
    from datetime import datetime, timedelta
    today = datetime.now().date()
    max_date = today + timedelta(days=30)
    
    return render(request, 'bookings/book.html', {
        'providers': providers,
        'selected_provider': selected_provider,
        'date': date,
        'slots': available_slots,
        'confirm_slot': confirm_slot,
        'today': today,
        'max_date': max_date,
        'appointment_types': Appointment.APPOINTMENT_TYPES,
    })

@login_required
def booking_confirmation(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id, customer=request.user)
    return render(request, 'bookings/confirmation.html', {'appointment': appt})

@login_required
def availability_list(request):
    if not request.user.is_provider():
        return redirect('dashboard')
    availabilities = Availability.objects.filter(provider=request.user)
    return render(request, 'bookings/availability_list.html', {'availabilities': availabilities})

@login_required
def availability_create(request):
    if not request.user.is_provider():
        return redirect('dashboard')
    message = None
    if request.method == 'POST':
        date = request.POST.get('date')
        start = request.POST.get('start')
        end = request.POST.get('end')
        interval = request.POST.get('interval', '30')
        from datetime import datetime as dt
        try:
            date_obj = dt.strptime(date, '%Y-%m-%d').date()
            start_t = dt.strptime(start, '%H:%M').time()
            end_t = dt.strptime(end, '%H:%M').time()
            interval_val = int(interval)
            if end_t <= start_t:
                message = 'End must be after start.'
            elif interval_val not in (10, 15, 20, 30, 45, 60):
                message = 'Invalid interval.'
            else:
                start_dt = dt.combine(date_obj, start_t)
                end_dt = dt.combine(date_obj, end_t)
                overlap_slots = Slot.objects.filter(provider=request.user, start_time__lt=end_dt, end_time__gt=start_dt)
                if overlap_slots.exists():
                    message = 'Overlaps existing slots.'
                else:
                    availability = Availability.objects.create(provider=request.user, date=date_obj, start_time=start_t, end_time=end_t, interval_minutes=interval_val)
                    availability.generate_slots()
                    return redirect('availability_list')
        except ValueError:
            message = 'Invalid input.'
    return render(request, 'bookings/availability_create.html', {'message': message})

@login_required
def availability_edit(request, availability_id):
    if not request.user.is_provider():
        return redirect('dashboard')
    availability = get_object_or_404(Availability, id=availability_id, provider=request.user)
    message = None
    # if any generated slot for this availability is booked, restrict edits of times/interval
    related_slots = Slot.objects.filter(provider=request.user, start_time__date=availability.date)
    has_booked = related_slots.filter(is_booked=True).exists()
    if request.method == 'POST':
        if has_booked:
            message = 'Cannot modify times—one or more slots already booked.'
        else:
            date = request.POST.get('date')
            start = request.POST.get('start')
            end = request.POST.get('end')
            interval = request.POST.get('interval', availability.interval_minutes)
            from datetime import datetime as dt
            try:
                date_obj = dt.strptime(date, '%Y-%m-%d').date()
                start_t = dt.strptime(start, '%H:%M').time()
                end_t = dt.strptime(end, '%H:%M').time()
                interval_val = int(interval)
                if end_t <= start_t:
                    message = 'End must be after start.'
                elif interval_val not in (10,15,20,30,45,60):
                    message = 'Invalid interval.'
                else:
                    availability.date = date_obj
                    availability.start_time = start_t
                    availability.end_time = end_t
                    availability.interval_minutes = interval_val
                    availability.save()
                    # regenerate slots (delete old free slots only) when editing
                    Slot.objects.filter(provider=request.user, start_time__date=availability.date, is_booked=False).delete()
                    availability.generate_slots()
                    return redirect('availability_list')
            except ValueError:
                message = 'Invalid input.'
    return render(request, 'bookings/availability_edit.html', {
        'availability': availability,
        'message': message,
        'has_booked': has_booked,
    })

@login_required
def availability_delete(request, availability_id):
    if not request.user.is_provider():
        return redirect('dashboard')
    availability = get_object_or_404(Availability, id=availability_id, provider=request.user)
    # Disallow delete if any slot for that window is booked
    related_slots = Slot.objects.filter(provider=request.user, start_time__date=availability.date)
    if related_slots.filter(is_booked=True).exists():
        # redirect with flash? simple message page for now
        return render(request, 'bookings/availability_delete.html', {'availability': availability, 'blocked': True})
    if request.method == 'POST':
        # delete availability and its free slots for that date
        Slot.objects.filter(provider=request.user, start_time__date=availability.date, is_booked=False).delete()
        availability.delete()
        return redirect('availability_list')
    return render(request, 'bookings/availability_delete.html', {'availability': availability, 'blocked': False})
