from django.db import models
from datetime import timedelta

# ------------------------------------------------------
# PREGNANT WOMAN MODEL
# ------------------------------------------------------
class PregnantWoman(models.Model):
    RISK_CHOICES = [
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Low', 'Low'),
    ]

    # --- Basic Information ---
    full_name = models.CharField(max_length=200, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    age = models.IntegerField(blank=False, null=False)

    # --- Location ---
    county = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)

    # --- Medical Details ---
    lmp = models.DateField(verbose_name="Last Menstrual Period", blank=False, null=False)
    
    # This is the Mother's calculated due date
    expected_due_date = models.DateField(verbose_name="Expected Delivery Date", blank=True, null=True)

    blood_type = models.CharField(max_length=10, blank=True, null=True)

    gravida = models.IntegerField(default=1, blank=True, null=True)
    parity = models.IntegerField(default=0, blank=True, null=True)

    primary_reason = models.CharField(max_length=255, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    risk_level = models.CharField(
        max_length=50,
        choices=RISK_CHOICES,
        default="Normal"
    )

    # --- Emergency Contact ---
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatic Logic: If LMP is provided but Due Date is missing, calculate it (LMP + 280 days)
        if self.lmp and not self.expected_due_date:
            self.expected_due_date = self.lmp + timedelta(days=280)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


# ------------------------------------------------------
# APPOINTMENT MODEL
# ------------------------------------------------------
class Appointment(models.Model):
    patient = models.ForeignKey(
        PregnantWoman,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    date = models.DateField()
    time = models.TimeField()
    purpose = models.CharField(max_length=200, help_text="Reason for visit")
    notes = models.TextField(blank=True, null=True)
    doctor = models.CharField(max_length=100, null=True, blank=True)

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.date}"


# ------------------------------------------------------
# DELIVERY MODEL
# ------------------------------------------------------
class Delivery(models.Model):
    DELIVERY_TYPES = [
        ('Normal Delivery', 'Normal Delivery'),
        ('C-Section', 'C-Section'),
        ('Assisted Delivery', 'Assisted Delivery'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    patient = models.ForeignKey(
        PregnantWoman,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    
    emergency_contact = models.CharField(
        max_length=255, 
        help_text="Emergency Contact Name, Relationship & Phone", 
        null=True, 
        blank=True
    )

    # --- DATES ---
    edd = models.DateField(verbose_name="Expected Date of Delivery", null=True, blank=True)
    delivery_date = models.DateField(verbose_name="Actual Delivery Date")
    delivery_time = models.TimeField(null=True, blank=True)
    
    # --- BABY DETAILS ---
    baby_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    baby_weight = models.DecimalField(max_digits=4, decimal_places=2, help_text="Weight in kg", null=True, blank=True)
    attending_physician = models.CharField(max_length=100, null=True, blank=True)

    delivery_type = models.CharField(max_length=50, choices=DELIVERY_TYPES)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # SMART LOGIC: If user didn't fill in EDD on the delivery form, 
        # grab it from the Mother's record automatically.
        if not self.edd and self.patient and self.patient.expected_due_date:
            self.edd = self.patient.expected_due_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Delivery - {self.patient.full_name} ({self.delivery_type})"


# ------------------------------------------------------
# DISCHARGE MODEL
# ------------------------------------------------------
class Discharge(models.Model):
    CONDITION_CHOICES = [
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Critical', 'Critical'),
        ('Deceased', 'Deceased'),
    ]

    BILLING_CHOICES = [
        ('Pending Clearance', 'Pending Clearance'),
        ('Cleared', 'Cleared'),
        ('Insurance Pending', 'Insurance Pending'),
    ]

    patient = models.ForeignKey(
        PregnantWoman,
        on_delete=models.CASCADE,
        related_name='discharges'
    )

    admission_date = models.DateField(null=True, blank=True)
    discharge_date = models.DateField()
    discharged_by = models.CharField(max_length=100, null=True, blank=True)
    
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)

    billing_status = models.CharField(
        max_length=50, 
        choices=BILLING_CHOICES, 
        default='Pending Clearance'
    )

    medications = models.TextField(
        blank=True, 
        null=True, 
        help_text="List prescriptions and medications"
    )
    
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discharge - {self.patient.full_name} ({self.condition})"


# ------------------------------------------------------
# NEW: TRANSACTION MODEL (For M-Pesa & Billing)
# ------------------------------------------------------
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]

    patient = models.ForeignKey(
        PregnantWoman,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - KES {self.amount} ({self.status})"