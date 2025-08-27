from django.urls import path
from .views import *


app_name = 'Law'

urlpatterns = [
    path('',HomeView,name='chome'),
    path('lhome',LawyerHome,name='lhome'),
    path('ahome',AdminHome,name='ahome'),
    path('about/',AboutView,name='about'),
<<<<<<< HEAD
    path('dashboard/',dashboard,name='dashboard'),
=======
>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024
    path('view_clients/', view_clients, name='clientview'),
    path('view_lawyers/', view_lawyers, name='lawyerview'),
    path('view_appointments/', view_appointments, name='appointmentview'),
    path('verify-lawyer/<int:pk>/',verify_lawyer, name='verify_lawyer'),
    path('delete-lawyer/<int:id>/',delete_lawyer, name='delete_lawyer'),
    path('delete_client/<int:id>/',delete_client, name='delete_client'),
<<<<<<< HEAD
    path('bills/',billview, name='billview'),
    path('invoice/<int:payment_id>/download/',download_invoice, name='download_invoice'),
=======
>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024
    path('logout/', logout_view, name='logoutadmin'),

]