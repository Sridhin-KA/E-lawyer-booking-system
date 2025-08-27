from django.urls import path
from . import views

app_name = 'lawyer'

urlpatterns = [
    path('view-appointments/', views.view_appointments, name='view_lawyer_appointments'),
    path('update-appointment/<int:appointment_id>/', views.update_appointment_status, name='update_appointment'),
    # path('lawyer-chat/', views.lawyer_chat, name='lawyer_chat'),
    # path('get-chat-history/<int:client_id>/', views.get_chat_history, name='get_chat_history'),
    # path('send-message/', views.send_message, name='send_message'),
    path('lawyer-chat/', views.lawyer_chat, name='lawyer_chat'),
    path('lawyer/get-messages/<str:client_name>/', views.get_messages, name='get_messages'),
    path('lawyer/send-message/', views.send_message, name='send_message'),
    path('send_message/<int:client_id>/', views.send_message_to_client, name='send_message_to_client'),
    path('start-video-call/', views.start_video_call, name='start_video_call'),
    path('create_room/', views.create_room, name='create_room'),
    path('join_room/', views.join_room, name='join_room'),
    path('room/<str:room_number>/', views.video_call_room, name='video_call_room'),
    path('vault',views.lawyer_vault,name='vault'),

    path('lawyer_profile',views.lawyer_profile,name='lawyer_profile'),
    path('status/', views.case_status_view, name='status'), 
    path('update_case_status/<int:appointment_id>/', views.update_case_status, name='update_case_status'),   




]