from django.urls import path
from .views import *


app_name = 'Law'

urlpatterns = [
    path('',HomeView,name='chome'),
    path('lhome',LawyerHome,name='lhome'),
    path('ahome',AdminHome,name='ahome'),
    path('about/',AboutView,name='about'),

    path('dashboard/',dashboard,name='dashboard'),

    path('view_clients/', view_clients, name='clientview'),
    path('view_lawyers/', view_lawyers, name='lawyerview'),
    path('view_appointments/', view_appointments, name='appointmentview'),
    path('verify-lawyer/<int:pk>/',verify_lawyer, name='verify_lawyer'),
    path('delete-lawyer/<int:id>/',delete_lawyer, name='delete_lawyer'),
    path('delete_client/<int:id>/',delete_client, name='delete_client'),

    path('bills/',billview, name='billview'),
    path('invoice/<int:payment_id>/download/',download_invoice, name='download_invoice'),
    path('logout/', logout_view, name='logoutadmin'),

]