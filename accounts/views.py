from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from bookings.models import Appointment
from .forms import UserRegisterForm
from .models import User


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    context = {}
    now = timezone.now()
    if request.user.is_provider():
        provider_appts = Appointment.objects.filter(slot__provider=request.user)
        context['pending_requests'] = provider_appts.filter(status='pending')[:10]
        context['upcoming_approved'] = provider_appts.filter(status='approved', slot__start_time__gte=now)[:10]
        template = 'accounts/dashboard_provider.html'
    else:
        my_appts = Appointment.objects.filter(customer=request.user)
        context['upcoming'] = my_appts.filter(status__in=['pending','approved'], slot__start_time__gte=now)[:10]
        context['past'] = my_appts.filter(slot__start_time__lt=now).exclude(status='cancelled')[:10]
        template = 'accounts/dashboard_customer.html'
    return render(request, template, context)

@login_required
def providers_list(request):
    providers = User.objects.filter(role='provider')
    q = request.GET.get('q')
    if q:
        from django.db.models import Q
        providers = providers.filter(Q(username__icontains=q) | Q(specialty__icontains=q))
    return render(request, 'accounts/providers_list.html', {'providers': providers, 'q': q})

def auth_combined(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    reg_form = UserRegisterForm(prefix='reg')
    login_form = AuthenticationForm(request, prefix='log')
    active_tab = 'login'
    if request.method == 'POST':
        if 'reg-username' in request.POST:
            reg_form = UserRegisterForm(request.POST, prefix='reg')
            if reg_form.is_valid():
                user = reg_form.save()
                login(request, user)
                return redirect('dashboard')
            active_tab = 'register'
        elif 'log-username' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST, prefix='log')
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('dashboard')
            active_tab = 'login'
    return render(request, 'accounts/auth.html', {
        'reg_form': reg_form,
        'login_form': login_form,
        'active_tab': active_tab
    })
