from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from E_lawyer.client.models import Appointment, LawyerDetails,ClientDetails,Payment
from django.views.decorators.http import require_POST
from .models import *
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import random
import string
from django.http import Http404
from django.core.mail import send_mail
from django.conf import settings
<<<<<<< HEAD
from django.contrib import messages
=======
>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024





@login_required
def view_appointments(request):
    try:
        lawyer = LawyerDetails.objects.get(id=request.user.id)
    except LawyerDetails.DoesNotExist:
        return HttpResponse("Invalid Account")
    appointments = Appointment.objects.filter(lawyer=lawyer).order_by('-appointment_date', '-appointment_time')

    return render(request, 'client/view_lawyer_appointment.html', {'appointments': appointments})

@require_POST
@login_required
def update_appointment_status(request, appointment_id):
    new_status = request.POST.get('status')
    lawyer = LawyerDetails.objects.get(id=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, lawyer=lawyer)
    appointment.status = new_status
    appointment.save()
    return redirect('lawyer:view_lawyer_appointments')


def lawyer_chat(request):
    try:
        # Fetch the current lawyer's details
        lawyer = LawyerDetails.objects.get(id=request.user.id)

        # Get only the clients who have paid appointments with the logged-in lawyer
        appointments = Appointment.objects.filter(lawyer=lawyer, status='Paid')
        client_ids = appointments.values_list('user', flat=True).distinct()
        clients = ClientDetails.objects.filter(id__in=client_ids)

        selected_client = None
        messages = []

        # Check if a client is selected via URL
        client_id = request.GET.get('client_id')
        if client_id:
            try:
                selected_client = ClientDetails.objects.get(pk=int(client_id))

                # Fetch messages between logged-in lawyer and the selected client
                messages = Message.objects.filter(
                    Q(sender=request.user, receiver=selected_client.id) |
                    Q(sender=selected_client.id, receiver=request.user)
                ).order_by('timestamp')  # Assuming you want to sort by timestamp

            except (ClientDetails.DoesNotExist, ValueError):
                selected_client = None

        return render(request, 'client/lawyer_chat.html', {
            'clients': clients,
            'selected_client': selected_client,
            'messages': messages,
        })

    except LawyerDetails.DoesNotExist:
        return render(request, 'client/lawyer_chat.html', {
            'clients': [],
            'selected_client': None,
            'messages': [],
        })
@login_required
def get_messages(request, client_name):
    try:
        # Fetch client based on client_name (e.g., "joe")
        client = ClientDetails.objects.get(username=client_name)
        messages = Message.objects.filter(receiver=client.user).values('sender__username', 'message', 'created_at')
        return JsonResponse({'status': 'success', 'messages': list(messages)})
    except ClientDetails.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Client not found'}, status=404)

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_name = data.get('client_name')
            message_content = data.get('message')

            if not message_content:
                return JsonResponse({'status': 'error', 'message': 'Message content is required'}, status=400)

            # Fetch the client by username or another unique identifier
            try:
                client = ClientDetails.objects.get(username=client_name)
                # Get the associated User instance
                user = client.user  # Assuming a ForeignKey to User is in ClientDetails model
            except ClientDetails.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Client not found'}, status=404)

            # Save the message to the database
            message = Message.objects.create(
                sender=request.user,
                receiver=user,  # Assign the User instance here
                message=message_content,
            )

            return JsonResponse({'status': 'success', 'message': 'Message sent'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
# @login_required
# def get_chat_history(request, client_id):
#     try:
#         lawyer = LawyerDetails.objects.get(user=request.user)
#         client = ClientDetails.objects.get(id=client_id)

#         messages = Message.objects.filter(client=client, lawyer=lawyer).order_by('timestamp')

#         msg_list = [{
#             'sender': msg.sender.username,
#             'message': msg.message,
#             'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M')
#         } for msg in messages]

#         return JsonResponse({'messages': msg_list})
#     except:
#         return JsonResponse({'messages': []})
@login_required
def send_message_to_client(request, client_id):
    if request.method == 'POST':
        lawyer = LawyerDetails.objects.get(id=request.user.id)
        client = get_object_or_404(ClientDetails, pk=client_id)

        message_text = request.POST.get('message')

        if message_text:
            Message.objects.create(
                sender=request.user,
                receiver=client.id,
                message=message_text,
                client=client,
                lawyer=lawyer,
            )

    return redirect('lawyer:lawyer_chat')  # or redirect back to the same client_id if you want


@login_required
def start_video_call(request):
    return render(request, 'client/start_call.html')
@login_required
def create_room(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')  # Get client ID from form
        if not client_id:
            return redirect('lawyer:start_call')  # fallback if client_id missing

        client = ClientDetails.objects.get(first_name=client_id)

        # Create random room number
        room_number = random.randint(100000, 999999)

        # Create room in database
        room = VideoCallRoom.objects.create(
            lawyer=request.user,
            client=client.id,
            room_id=room_number
        )

        # Send email to client
        subject = 'Video Call Invitation'
        message = f'Hello {client.first_name},\n\nYou are invited to a video call.\n\nRoom Number: {room_number}\n\nPlease join the room using the app.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [client.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # 🎯 After creating the room, directly go to video call room page:
        return redirect('lawyer:video_call_room', room_number=room_number)

    return redirect('lawyer:start_call')

def join_room(request):
    """
    This view allows clients to join a video call room.
    """
    if request.method == "POST":
        room_number = request.POST.get('room_number')
        try:
            room = VideoCallRoom.objects.get(room_id=room_number)

            # Check if the client is allowed to join (check if the room is waiting)
            if room.status == 'waiting':
                
                room.save()

                # Add the client as a participant
                room.status = 'accepted'
                room.save()

                return redirect('lawyer:video_call_room', room_number=room.room_id)
            else:
                return render(request, 'client/join_room.html', {'error': "The room is no longer available."})

        except VideoCallRoom.DoesNotExist:
            return render(request, 'client/join_room.html', {'error': "Room not found."})

    return render(request, 'client/join_room.html')


def video_call_room(request, room_number):
    """
    This view renders the video call room page with the specified room number.
    """
    # Retrieve the room from the database
    try:
        room = VideoCallRoom.objects.get(room_id=room_number)
    except VideoCallRoom.DoesNotExist:
        raise Http404("Room not found")

    # Ensure the user is either the lawyer or the client of the room
    if request.user not in [room.lawyer, room.client]:
        raise Http404("You are not authorized to access this room")

    # If the user is the client, allow them to join the room
    if room.status == 'waiting' and room.client is None:
        return redirect('lawyer:join_room')

    # Handle other room statuses
    room_details = {
        'room_number': room.room_id,
        'status': room.status,
        'lawyer': room.lawyer,
        'client': room.client,
    }

    print(f"Room Details: {room_details}")  # Debugging line

    return render(request, 'client/video_call_room.html', room_details)

@login_required
def lawyer_vault(request):
    if not hasattr(request.user, 'lawyerdetails'):
        return redirect('home')  # Prevent non-lawyers

    if request.method == 'POST':
        file = request.FILES.get('file')
        client_id = request.POST.get('client')
        client = User.objects.get(id=client_id) if client_id else None

        if file and client:
            VaultFile.objects.create(
                client=client,
                lawyer=request.user,
                file=file,
                filename=file.name
            )
            return redirect('lawyer:vault')

    # Files uploaded TO the lawyer by clients
    received_files = VaultFile.objects.filter(lawyer=request.user)

    # Clients with whom this lawyer had 'Paid' appointments
    paid_appointments = Appointment.objects.filter(lawyer__id=request.user.id, status='Paid')
    paid_clients = User.objects.filter(id__in=paid_appointments.values_list('user__id', flat=True))

    return render(request, 'client/vault.html', {
        'files': received_files,
        'clients': paid_clients
    })
<<<<<<< HEAD

@login_required
def lawyer_profile(request):
    lawyer = LawyerDetails.objects.get(id=request.user)

    if request.method == 'POST':
        lawyer.first_name = request.POST.get('first_name')
        lawyer.last_name = request.POST.get('last_name')
        lawyer.phone = request.POST.get('phone')
        lawyer.category = request.POST.get('category')

        if 'photo' in request.FILES:
            lawyer.photo = request.FILES['photo']

        lawyer.save()
        messages.success(request, "Profile updated successfully.")

    return render(request, 'client/lawyer_profile.html', {'lawyer': lawyer})


@login_required
def case_status_view(request):
    lawyer = request.user.lawyerdetails
    appointments = Appointment.objects.filter(lawyer=lawyer, status='Paid')
    return render(request, 'client/case_status.html', {'appointments': appointments})

@login_required
def update_case_status(request, appointment_id):
    try:
        lawyer = request.user.lawyerdetails
        appointment = get_object_or_404(Appointment, id=appointment_id, lawyer=lawyer)
        if request.method == "POST":
            new_status = request.POST.get("case_status")
            appointment.case_status = new_status
            appointment.save()
            messages.success(request, "Case status updated successfully.")
        return redirect('lawyer:status')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('lawyer:status')
=======
>>>>>>> 8c18ded32e8fc8b4a9705899026da72319422024
