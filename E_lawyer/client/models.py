from django.db import models
from django.contrib.auth.models import User,AbstractUser


# Create your models here.
class ClientDetails(models.Model):
    id = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.BigIntegerField(unique=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='customer/',null=True,blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class LawyerDetails(models.Model):
    id = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.BigIntegerField(unique=True)
    email = models.EmailField(unique=True)
    category = models.CharField(max_length=20)
    license_number = models.CharField(max_length=20)
    address = models.CharField(max_length=150)
    is_verified = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='customer/',null=True,blank=True)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

<<<<<<< HEAD

=======
>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('Paid','Paid'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

<<<<<<< HEAD
    CASE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('in progress 10%', 'In Progress (10%)'),
        ('in progress 30%', 'In Progress (30%)'),
        ('in progress 50%', 'In Progress (50%)'),
        ('in progress 80%', 'In Progress (80%)'),
    ]

=======
>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lawyer = models.ForeignKey('LawyerDetails', on_delete=models.CASCADE)
    issue = models.TextField()
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_mode = models.CharField(max_length=10, choices=[('online', 'Online'), ('offline', 'Offline')])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
<<<<<<< HEAD
    case_status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='pending')
=======

>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024
    class Meta:
        unique_together = ('lawyer', 'appointment_date', 'appointment_time')

    def __str__(self):
        return f"Appointment with {self.lawyer.first_name} on {self.appointment_date}"
    

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lawyer = models.ForeignKey(LawyerDetails, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_payment_id = models.CharField(max_length=255)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_signature = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.user.username} for Appointment ID {self.appointment.id}"
    

class VaultFile(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_files')
    file = models.FileField(upload_to='vault_uploads/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename