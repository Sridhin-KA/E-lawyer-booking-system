from django.contrib import admin
from django.utils.translation import gettext_lazy as _


# Register your models here.

admin.site.site_header = 'My Hospital Admin'  # Custom header
admin.site.site_title = 'Hospital Admin'     # Custom title
admin.site.index_title = 'Welcome to the Admin Dashboard'