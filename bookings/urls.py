from django.urls import path
from . import views

urlpatterns = [
    path('slots/', views.slot_list, name='slot_list'),
    path('slots/create/', views.slot_create, name='slot_create'),
    path('slots/<int:slot_id>/edit/', views.slot_edit, name='slot_edit'),
    path('slots/<int:slot_id>/delete/', views.slot_delete, name='slot_delete'),
    path('providers/<int:provider_id>/slots/', views.provider_slots, name='provider_slots'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/<str:action>/', views.appointment_action, name='appointment_action'),
    path('approve/<int:appointment_id>/', views.appointment_action, {'action':'approve'}, name='appointment_approve'),
    path('reject/<int:appointment_id>/', views.appointment_action, {'action':'reject'}, name='appointment_reject'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('api/providers/<int:provider_id>/slots/', views.api_available_slots, name='api_available_slots'),
    path('book/', views.booking_wizard, name='booking_wizard'),
    path('confirmation/<int:appointment_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('availability/', views.availability_list, name='availability_list'),
    path('availability/create/', views.availability_create, name='availability_create'),
    path('availability/<int:availability_id>/edit/', views.availability_edit, name='availability_edit'),
    path('availability/<int:availability_id>/delete/', views.availability_delete, name='availability_delete'),
]
