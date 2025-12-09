from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'patients'

urlpatterns = [
    # --- Authentication URLs ---
    
    # 1. ROOT URL IS NOW LOGIN
    path('', auth_views.LoginView.as_view(template_name='patients/login.html', redirect_authenticated_user=True), name='login'),

    # Logout now redirects explicitly back to the 'login' page defined above
    path('logout/', auth_views.LogoutView.as_view(next_page='patients:login'), name='logout'),

    # --- Dashboard ---
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Patients ---
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/edit/<int:id>/', views.edit_patient, name='edit_patient'),
    path('patients/delete/<int:id>/', views.delete_patient, name='delete_patient'),

    # --- Appointments ---
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/edit/<int:id>/', views.edit_appointment, name='edit_appointment'),
    path('appointments/delete/<int:id>/', views.delete_appointment, name='delete_appointment'),

    # --- Deliveries ---
    path('deliveries/add/', views.add_delivery, name='add_delivery'),
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/edit/<int:id>/', views.edit_delivery, name='edit_delivery'),
    path('deliveries/delete/<int:id>/', views.delete_delivery, name='delete_delivery'),

    # --- Discharges ---
    path('discharges/add/', views.add_discharge, name='add_discharge'),
    path('discharges/', views.discharge_list, name='discharge_list'),
    path('discharges/edit/<int:id>/', views.edit_discharge, name='edit_discharge'),
    path('discharges/delete/<int:id>/', views.delete_discharge, name='delete_discharge'),

    # --- Billing & Payments (NEW) ---
    # This loads the page
    path('billing/', views.billing_view, name='billing_page'),
    # This handles the form submission (Charge button)
    path('billing/initiate/', views.initiate_stk_push, name='initiate_stk_push'),
]