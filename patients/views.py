from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages 
from django.db.models import Q, Sum
from django.utils import timezone 
import datetime
from django.contrib.auth.decorators import login_required

# IMPORTS: 
from .models import PregnantWoman, Appointment, Delivery, Discharge, Transaction
from .forms import PregnantWomanForm, AppointmentForm, DeliveryForm, DischargeForm

# ==========================================
# Dashboard
# ==========================================
def dashboard(request):
    today = timezone.now().date()

    # --- 1. Basic Stats ---
    total_patients = PregnantWoman.objects.count()
    high_risk_patients = PregnantWoman.objects.filter(risk_level='High').count()
    upcoming_appointments = Appointment.objects.filter(status='Scheduled', date__gte=today).count()
    total_deliveries = Delivery.objects.count()
    total_discharges = Discharge.objects.count()
    
    # Calculate Total Revenue from Success Transactions
    revenue_this_month = Transaction.objects.filter(
        status='Success', 
        created_at__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # --- 2. Missed Appointments ---
    missed_appointments = Appointment.objects.filter(status='Scheduled', date__lt=today).count()

    # --- 3. Urgent Patient Logic ---
    urgent_patient = PregnantWoman.objects.filter(
        risk_level='High',
        expected_due_date__isnull=False
    ).order_by('expected_due_date').first()

    # --- 4. Trimester Calculations ---
    t1_count = 0
    t2_count = 0
    t3_count = 0
    
    all_patients = PregnantWoman.objects.filter(expected_due_date__isnull=False)

    for patient in all_patients:
        if patient.expected_due_date:
            days_remaining = (patient.expected_due_date - today).days
            weeks_pregnant = 40 - (days_remaining / 7)

            if weeks_pregnant <= 12:
                t1_count += 1
            elif 12 < weeks_pregnant <= 27:
                t2_count += 1
            elif weeks_pregnant > 27:
                t3_count += 1

    total_calculated = t1_count + t2_count + t3_count
    
    if total_calculated > 0:
        t1_percent = round((t1_count / total_calculated) * 100)
        t2_percent = round((t2_count / total_calculated) * 100)
        t3_percent = round((t3_count / total_calculated) * 100)
    else:
        t1_percent = 0
        t2_percent = 0
        t3_percent = 0

    context = {
        'total_patients': total_patients,
        'high_risk_patients': high_risk_patients,
        'upcoming_appointments': upcoming_appointments,
        'total_deliveries': total_deliveries,
        'total_discharges': total_discharges,
        'revenue_this_month': revenue_this_month,
        'urgent_patient': urgent_patient,
        'missed_appointments': missed_appointments,
        'first_trimester': t1_count,
        'second_trimester': t2_count,
        'third_trimester': t3_count,
        'first_trimester_percent': t1_percent,
        'second_trimester_percent': t2_percent,
        'third_trimester_percent': t3_percent,
    }
    return render(request, 'patients/dashboard.html', context)

# ==========================================
# Patient Views
# ==========================================
def patient_list(request):
    search_query = request.GET.get('q')
    patients = PregnantWoman.objects.all().order_by('-created_at')
    
    if search_query:
        patients = patients.filter(
            Q(full_name__icontains=search_query) | 
            Q(phone__icontains=search_query)
        )
        
    return render(request, 'patients/patient_list.html', {'patients': patients})

def add_patient(request):
    if request.method == 'POST':
        form = PregnantWomanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient registered successfully!")
            return redirect('patients:patient_list')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = PregnantWomanForm()
    return render(request, 'patients/add_patient.html', {'form': form})

def edit_patient(request, id):
    patient = get_object_or_404(PregnantWoman, id=id)
    if request.method == 'POST':
        form = PregnantWomanForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient details updated successfully!")
            return redirect('patients:patient_list')
        else:
            messages.error(request, "Update failed. Please check the form.")
    else:
        form = PregnantWomanForm(instance=patient)
    return render(request, 'patients/edit_patient.html', {'form': form, 'patient': patient})

def delete_patient(request, id):
    patient = get_object_or_404(PregnantWoman, id=id)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Patient deleted successfully.")
        return redirect('patients:patient_list')
    return render(request, 'patients/delete_patient.html', {'patient': patient})


# ==========================================
# Appointment Views
# ==========================================
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('date', 'time')
    
    search_query = request.GET.get('q')
    if search_query:
        appointments = appointments.filter(
            Q(patient__full_name__icontains=search_query) | 
            Q(doctor__icontains=search_query) |
            Q(purpose__icontains=search_query) |
            Q(status__icontains=search_query)
        )

    return render(request, 'patients/appointments.html', {'appointments': appointments})

def add_appointment(request):
    patients = PregnantWoman.objects.all().order_by('full_name')
    context = {'patients': patients}
    initial_data = {}
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        purpose = request.POST.get('purpose')
        doctor = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        notes = request.POST.get('notes')
        
        initial_data = request.POST.copy()
        context['initial_data'] = initial_data
        
        try:
            patient_obj = get_object_or_404(PregnantWoman, id=patient_id)
            Appointment.objects.create(
                patient=patient_obj,
                purpose=purpose,
                doctor=doctor,
                date=date,
                time=time,
                notes=notes,
                status='Scheduled'
            )
            messages.success(request, "Appointment scheduled successfully!")
            return redirect('patients:appointment_list')
        except Exception as e:
            print(f"Error adding appointment: {e}")
            messages.error(request, "Failed to schedule appointment. Please check inputs.")
            
    return render(request, 'patients/add_appointment.html', context)

def edit_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    patients = PregnantWoman.objects.all().order_by('full_name')
    context = {'appointment': appointment, 'patients': patients}
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        purpose = request.POST.get('purpose')
        doctor = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        notes = request.POST.get('notes')
        
        try:
            patient_obj = get_object_or_404(PregnantWoman, id=patient_id)
            appointment.patient = patient_obj
            appointment.purpose = purpose
            appointment.doctor = doctor
            appointment.date = date
            appointment.time = time
            appointment.notes = notes
            appointment.status = 'Scheduled'
            appointment.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect('patients:appointment_list')
        except Exception as e:
            print(e)
            messages.error(request, "Failed to update appointment. Please check inputs.")
            
    return render(request, 'patients/edit_appointment.html', context)

def delete_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment cancelled.")
        return redirect('patients:appointment_list')
    return render(request, 'patients/delete_appointment.html', {'appointment': appointment})


# ==========================================
# Delivery Views
# ==========================================
def add_delivery(request):
    if request.method == "POST":
        data = request.POST.copy()
        e_name = request.POST.get('emergency_name', '')
        e_rel = request.POST.get('emergency_relationship', '')
        e_phone = request.POST.get('emergency_phone', '')

        if e_name: 
            combined_contact = f"{e_name} ({e_rel}) - {e_phone}"
            data['emergency_contact'] = combined_contact

        form = DeliveryForm(data)

        if form.is_valid():
            form.save()
            messages.success(request, "Delivery recorded successfully!")
            return redirect('patients:delivery_list')
        else:
            print("Delivery Form Errors:", form.errors)
            messages.error(request, "Failed to record delivery. Please check the inputs.")
    else:
        form = DeliveryForm()
    return render(request, 'patients/add_delivery.html', {'form': form})

def delivery_list(request):
    deliveries = Delivery.objects.all().order_by('-delivery_date')
    
    search_query = request.GET.get('q')
    if search_query:
        deliveries = deliveries.filter(
            Q(patient__full_name__icontains=search_query) |
            Q(blood_group__icontains=search_query) |
            Q(delivery_type__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    return render(request, 'patients/delivery_list.html', {'deliveries': deliveries})

def edit_delivery(request, id):
    delivery = get_object_or_404(Delivery, id=id)
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery updated successfully!")
            return redirect('patients:delivery_list') 
        else:
            messages.error(request, "Update failed. Please check the form.")
    else:
        form = DeliveryForm(instance=delivery)
    return render(request, 'patients/edit_delivery.html', {'form': form, 'delivery': delivery})

def delete_delivery(request, id):
    delivery = get_object_or_404(Delivery, id=id)
    if request.method == 'POST':
        delivery.delete()
        messages.success(request, "Delivery record deleted.")
        return redirect('patients:delivery_list')
    return render(request, 'patients/delete_delivery.html', {'delivery': delivery})


# ==========================================
# Discharge Views (UPDATED LOGIC HERE)
# ==========================================
def add_discharge(request):
    if request.method == "POST":
        form = DischargeForm(request.POST)
        if form.is_valid():
            # 1. Grab the instance but don't save yet
            discharge_instance = form.save(commit=False)
            patient = discharge_instance.patient

            # 2. CHECK IF BILL IS PAID
            # We look for at least one successful transaction for this patient.
            has_paid = Transaction.objects.filter(
                patient=patient, 
                status='Success'
            ).exists()

            # 3. Decision Logic
            if has_paid:
                discharge_instance.save()
                messages.success(request, f"Billing Cleared. Patient {patient.full_name} discharged successfully!")
                return redirect('patients:discharge_list')
            else:
                # 4. Block Discharge
                messages.error(request, f"⚠ DISCHARGE BLOCKED: Patient {patient.full_name} has outstanding bills. Payment required.")
                # We return the form with data so they don't have to re-type, but discharge is NOT saved.
                return render(request, 'patients/add_discharge.html', {'form': form})
                
        else:
            print("Discharge Form Errors:", form.errors)
            messages.error(request, "Failed to save discharge. Please check the form.")
    else:
        form = DischargeForm()
    return render(request, 'patients/add_discharge.html', {'form': form})

def discharge_list(request):
    discharges = Discharge.objects.all().order_by('-discharge_date')

    search_query = request.GET.get('q')
    if search_query:
        discharges = discharges.filter(
            Q(patient__full_name__icontains=search_query) |
            Q(condition__icontains=search_query) |
            Q(patient__phone__icontains=search_query)
        )

    return render(request, 'patients/discharge_list.html', {'discharges': discharges})

def edit_discharge(request, id):
    discharge = get_object_or_404(Discharge, id=id)
    if request.method == 'POST':
        form = DischargeForm(request.POST, instance=discharge)
        if form.is_valid():
            form.save()
            messages.success(request, "Discharge record updated!")
            return redirect('patients:discharge_list')
    else:
        form = DischargeForm(instance=discharge)
    return render(request, 'patients/edit_discharge.html', {'form': form, 'discharge': discharge})

def delete_discharge(request, id):
    discharge = get_object_or_404(Discharge, id=id)
    if request.method == 'POST':
        discharge.delete()
        messages.success(request, "Discharge record deleted.")
        return redirect('patients:discharge_list')
    return render(request, 'patients/delete_discharge.html', {'discharge': discharge})


# ==========================================
# Billing & Payment Views
# ==========================================

def billing_view(request):
    """
    Renders the billing page with patient dropdown and transaction history.
    """
    patients = PregnantWoman.objects.all().order_by('full_name')
    
    # Try to fetch transactions if the model exists, otherwise return empty list
    try:
        transactions = Transaction.objects.all().order_by('-created_at')[:15] 
    except NameError:
        transactions = []

    context = {
        'patients': patients,
        'transactions': transactions,
    }
    
    return render(request, 'patients/payment.html', context)

def initiate_stk_push(request):
    """
    Handles the form submission to initiate M-Pesa STK Push.
    """
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        amount = request.POST.get('amount')
        
        if not amount or amount == 'other':
             # Handle custom amount input if you have a field for it in HTML, otherwise default
            amount = 500 

        try:
            patient = get_object_or_404(PregnantWoman, id=patient_id)
            
            # --- SIMULATION OF M-PESA LOGIC ---
            Transaction.objects.create(
                patient=patient,
                amount=amount,
                status='Success', # In production, this would be 'Pending' then updated via Callback
                transaction_id=f"WS{datetime.datetime.now().strftime('%f')}" 
            )
            
            messages.success(request, f"STK Push of KES {amount} sent to {patient.full_name} ({patient.phone}) successfully. Payment Recorded.")
        
        except Exception as e:
            messages.error(request, f"Error initiating payment: {str(e)}")
            
        return redirect('patients:billing_page')
    
    return redirect('patients:billing_page')