from django import forms
from .models import PregnantWoman, Appointment, Delivery, Discharge


# ------------------------------------------------------
# PREGNANT WOMAN FORM
# ------------------------------------------------------
class PregnantWomanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            current_classes = widget.attrs.get('class', '')

            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue

            if isinstance(widget, forms.Select):
                widget.attrs['class'] = (current_classes + ' form-select').strip()
            else:
                widget.attrs['class'] = (current_classes + ' form-control').strip()

            if field.required:
                widget.attrs['required'] = 'required'

    class Meta:
        model = PregnantWoman
        fields = [
            'full_name', 'age', 'phone', 'email',
            'lmp', 'blood_type', 'risk_level', 'primary_reason',
            'emergency_contact_name',
            'emergency_contact_relation',
            'emergency_contact_phone',
            'medical_history'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'lmp': forms.DateInput(attrs={'type': 'date'}),
            'blood_type': forms.TextInput(attrs={'placeholder': 'e.g. O+'}),
            'risk_level': forms.Select(),
            'primary_reason': forms.TextInput(attrs={'placeholder': 'Primary Reason for Visit'}),
            'emergency_contact_name': forms.TextInput(attrs={'placeholder': 'Contact Name'}),
            'emergency_contact_relation': forms.TextInput(attrs={'placeholder': 'Relationship'}),
            'emergency_contact_phone': forms.TextInput(attrs={'placeholder': 'Contact Phone'}),
            'medical_history': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter any relevant medical history...'}),
        }


# ------------------------------------------------------
# APPOINTMENT FORM
# ------------------------------------------------------
class AppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            current_classes = widget.attrs.get('class', '')

            if isinstance(widget, forms.Select):
                widget.attrs['class'] = (current_classes + ' form-select').strip()
            elif not isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs['class'] = (current_classes + ' form-control').strip()

    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'time', 'purpose', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'purpose': forms.TextInput(attrs={'placeholder': 'Purpose of visit'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes'}),
        }


# ------------------------------------------------------
# DELIVERY FORM (UPDATED WITH EDD)
# ------------------------------------------------------
class DeliveryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            current_classes = widget.attrs.get('class', '')

            if isinstance(widget, forms.Select):
                widget.attrs['class'] = (current_classes + ' form-select').strip()
            else:
                widget.attrs['class'] = (current_classes + ' form-control').strip()

    class Meta:
        model = Delivery
        # Added 'edd' to the fields list below
        fields = [
            'patient', 'edd', 'delivery_date', 'delivery_time', 
            'delivery_type', 'attending_physician', 
            'baby_gender', 'baby_weight', 
            'blood_group', 'emergency_contact', 'notes'
        ]
        widgets = {
            'edd': forms.DateInput(attrs={'type': 'date'}),  # Added Widget for EDD
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_time': forms.TimeInput(attrs={'type': 'time'}),
            'attending_physician': forms.TextInput(attrs={'placeholder': 'e.g. Dr. Sarah Jones'}),
            'baby_weight': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'blood_group': forms.Select(),
            'emergency_contact': forms.TextInput(attrs={'placeholder': 'Name - Relation - Phone'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Complications or general delivery notes...'}),
        }


# ------------------------------------------------------
# DISCHARGE FORM (UPDATED)
# ------------------------------------------------------
class DischargeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Loop through fields to add Bootstrap classes automatically
        for field_name, field in self.fields.items():
            widget = field.widget
            current_classes = widget.attrs.get('class', '')

            if isinstance(widget, forms.Select):
                widget.attrs['class'] = (current_classes + ' form-select').strip()
            else:
                widget.attrs['class'] = (current_classes + ' form-control').strip()

    class Meta:
        model = Discharge
        fields = [
            'patient', 
            'admission_date', 
            'discharge_date', 
            'condition', 
            'billing_status',  # <--- Added
            'discharged_by', 
            'notes', 
            'medications'      # <--- Added
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'discharge_date': forms.DateInput(attrs={'type': 'date'}),
            'condition': forms.Select(),
            'billing_status': forms.Select(),  # Ensure this renders as a dropdown
            'discharged_by': forms.TextInput(attrs={'placeholder': 'Enter name'}),
            # Specific placeholders requested in the UI
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Patient condition upon discharge...'}),
            'medications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List medications...'}),
        }