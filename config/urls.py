from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse


def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),
    # Root convenience aliases
    path('register/', lambda r: redirect('auth_combined'), name='register_alias'),
    path('login/', lambda r: redirect('auth_combined'), name='login_alias'),
    path('dashboard/', lambda r: redirect('dashboard'), name='dashboard_alias'),
    path('appointments/', lambda r: redirect('appointment_list'), name='appointments_alias'),
    # Booking by provider id shortcut -> goes to wizard with provider preselected
    path('book/<int:provider>/', lambda r, provider: redirect(f"{reverse('booking_wizard')}?provider={provider}"), name='book_provider_alias'),
    path('', home, name='home'),
]
