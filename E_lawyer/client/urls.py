from django.urls import path

from .views import *


app_name = 'client'

urlpatterns = [
    path('register/',RegisterView,name='register'),
    path('lregister',lawyer_register,name='lregister'),
    path('login/',LoginView,name='login'),
    path('logout/',Logout,name='logout'),
    path('appointment/',appointment, name='appointment'),
    path('book-appointment/<int:lawyer_id>/',book_appointment, name='book_appointment'),
    path('view-appointment/',view_appointment, name='View_appointment'),
    path('pay_now/<int:appointment_id>/',initiate_payment, name='pay_now'),
    path('payment-success/',payment_success, name='payment_success'),
    path('chat/<str:username>/',chat_page, name='chat_page'),
    path('chat/<int:lawyer_id>/',chat_view, name='chat_view'),
    path('client/chat/<int:lawyer_id>/',client_chat, name='client_chat'),
    path('video-call-room/<str:room_code>/',video_call_room, name='actual_video_call_page'),
    path('start-video-call/<int:lawyer_id>/',start_video_call, name='start_video_call'),
    path('join-video-call/<str:room_code>/',join_video_call, name='join_video_call'),
    path('send-room-code-email/<str:room_id>/',send_room_code_email, name='send_room_code_email'),
    path('vault/',vaultopen, name='vaultopen'),
    path('profile/',client_profile, name='profile'),
    path('payments/',payments_view, name='payments'),
    path('download_invoice/<int:payment_id>/',download_invoice, name='download_invoice'),
    path('viewstatus/', viewstatus, name='viewstatus'),












]


    path('vault/',vaultopen, name='vaultopen')


    






]

