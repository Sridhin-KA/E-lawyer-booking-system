from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ClientDetails)
admin.site.register(LawyerDetails)
admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(VaultFile)