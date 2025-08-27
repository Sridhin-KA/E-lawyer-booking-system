from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth,messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import *
from .forms import *
from datetime import datetime, date, time
import razorpay
from razorpay import errors
from django.views.decorators.csrf import csrf_exempt
from E_lawyer.lawyer.models import *
from django.db.models import Q
import random
import string
from django.conf import settings
from django.http import HttpResponseServerError
from django.contrib.auth import authenticate, login

from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.contrib.auth import update_session_auth_hash
import json




# Create your views here.

def RegisterView(request):
    if request.method == 'POST':
        first_name = request.POST.get('c_fname')
        last_name = request.POST.get('c_lname')
        email = request.POST.get('c_email')
        phone = request.POST.get('c_phone')
        password = request.POST.get('c_password')
        re_password = request.POST.get('c_repassword')
        address = request.POST.get('c_address')
        photo = request.FILES.get('c_image')

        if password != re_password:
            messages.error(request,'Password do not match')
            return redirect('client:register')

        if User.objects.filter(email=email).exists():
            messages.error(request,'Email already exist')
            return redirect('client:register')

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request,'Phone number must be 10 digits')
            return redirect('client:register')
        try:
            user = User.objects.create_user(
                username=first_name,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            customer = ClientDetails(
                id=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                address=address,
                photo=photo
            )
            customer.save()

            subject = 'Registration Successful'
            message = f'Hi {user.username},\n\n Your registration was successful!'
            email_form = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, email_form, recipient_list)


            messages.success(request,'Registration successful')
            return redirect('client:login')
        except Exception as e:
            messages.error(request,f'an error occured:{e}')
            return redirect('client:register')
    return render(request,'client/register.html')


def lawyer_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('c_fname')
        last_name = request.POST.get('c_lname')
        email = request.POST.get('c_email')
        phone = request.POST.get('c_phone')
        password = request.POST.get('c_password')
        re_password = request.POST.get('c_repassword')
        lnum = request.POST.get('l_number')
        address = request.POST.get('c_address')
        photo = request.FILES.get('p_image')
        category = request.POST.get('lawyer_category')
        other_category = request.POST.get('other_category')
        final_category = other_category if category == 'other' else category 


        if password != re_password:
            messages.error(request,'Password do not match')
            return redirect('client:lregister')

        if User.objects.filter(email=email).exists():
            messages.error(request,'Email already exist')
            return redirect('client:lregister')

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request,'Phone number must be 10 digits')
            return redirect('client:lregister')
        try:
            user = User.objects.create_user(
                username=first_name,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            customer = LawyerDetails(
                id=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                address=address,
                license_number=lnum,
                category=final_category,
                photo=photo
            )
            customer.save()

            subject = 'Registration Successful'
            message = f'Hi {user.username},\n\n Your registration was successful!'
            email_form = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, email_form, recipient_list)


            messages.success(request,'Registration successful')
            return redirect('client:login')
        except Exception as e:
            messages.error(request,f'an error occured:{e}')
            return redirect('client:lregister')
    return render(request,'client/lregister.html')
def LoginView(request):
    if request.method == 'POST':
        uname = request.POST.get('c_fname')
        password = request.POST.get('c_password')

        # Admin login
        if uname == 'admin' and password == 'admin':
            request.session['admin_logged_in'] = True
            return redirect('Law:ahome')

        # Authenticate Django user
        user = authenticate(username=uname, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin/')

            # Check if user is a client
            if ClientDetails.objects.filter(id=user.id).exists():
                login(request, user)
                return redirect('Law:chome')

            # Check if user is a lawyer
            elif LawyerDetails.objects.filter(id=user.id).exists():
                lawyer = LawyerDetails.objects.get(id=user.id)
                if lawyer.is_verified:
                    login(request, user)
                    return redirect('Law:lhome')
                else:
                    messages.warning(request, 'Your account is not yet verified by the admin.')
                     # optional: redirect back to login

            else:
                messages.error(request, 'This account is not registered as a client or lawyer.')

        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'client/login.html')


def Logout(request):
    auth.logout(request)
    messages.error(request,'Logout Successful')
    return redirect('/client/login')


def appointment(request):
    category = request.GET.get('category', '')

    if category:
        if category.lower() == 'other':
            # Fetch lawyers whose category is neither 'criminal', 'civil', nor 'corporate'
            lawyers = LawyerDetails.objects.exclude(category__in=['Criminal', 'Civil', 'Corporate'])
        else:
            # Fetch lawyers with the selected category
            lawyers = LawyerDetails.objects.filter(category__iexact=category)  # Case-insensitive
    else:
        # Fetch all lawyers if no category is selected
        lawyers = LawyerDetails.objects.all()

    today = date.today().isoformat()

    return render(request, 'client/appointment.html', {
        'lawyers': lawyers,
        'selected_category': category,
        'today': today
    })


@login_required
def book_appointment(request, lawyer_id):
    lawyer = LawyerDetails.objects.get(id=lawyer_id)
    if request.method == 'POST':
        issue = request.POST.get('issue')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        appointment_mode = request.POST.get('appointment_mode')
        
        # Convert strings to proper datetime objects
        appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        appt_time = datetime.strptime(appointment_time, "%H:%M").time()

        # Validate past date
        if appt_date < date.today():
            messages.error(request, "Cannot book a past date.")
            return redirect('client:appointment')

        # Check if slot already booked
        if Appointment.objects.filter(lawyer=lawyer, appointment_date=appt_date, appointment_time=appt_time).exists():
            messages.error(request, "Time slot already booked!")
            return redirect('client:appointment')

        Appointment.objects.create(
            user=request.user,
            lawyer=lawyer,
            issue=issue,
            appointment_date=appt_date,
            appointment_time=appt_time,
            appointment_mode=appointment_mode,
            status='Pending'
        )

        messages.success(request, "Appointment booked successfully!")
        return redirect('client:View_appointment')

    return redirect('client:appointment')

def view_appointment(request):
    appointments = Appointment.objects.filter(user=request.user)
    context = {
        'appointments': appointments
    }
    return render(request, 'client/view_appointment.html', context)


@login_required
def initiate_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order_amount = 50000  
    order_currency = 'INR'

    try:
        order = client.order.create({
            'amount': order_amount,
            'currency': order_currency,
            'payment_capture': '1'
        })

        Payment.objects.create(
            user=request.user,
            lawyer=appointment.lawyer,
            appointment=appointment,
            amount=order_amount / 100,
            razorpay_order_id=order['id']
        )

        context = {
            'appointment': appointment,
            'order_id': order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': order_amount,
            'lawyer': appointment.lawyer
        }
        return render(request, 'client/payment_page.html', context)

    except errors.BadRequestError as e:
        return HttpResponse(f"Bad Request Error: {str(e)}", status=400)
    except errors.ServerError as e:
        return HttpResponse(f"Razorpay Server Error: {str(e)}", status=500)
    except Exception as e:
        return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        payment = Payment.objects.filter(razorpay_order_id=order_id).first()
        if payment:
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.paid = True
            payment.save()

            # Optional: update appointment status
            appointment = payment.appointment
            appointment.status = 'Paid'
            appointment.save()

            lawyer_details = LawyerDetails.objects.get(email=appointment.lawyer.email)
            return redirect('client:chat_page', username=lawyer_details.id.username)
            

    return redirect('client:view_appointment')


@login_required
def chat_view(request, lawyer_id):
    lawyer = User.objects.get(id=lawyer_id)
    client = request.user

    # Handle file upload
    if request.method == 'POST' and 'vault_upload' in request.POST:
        uploaded_file = request.FILES.get('vault_file')
        if uploaded_file:
            VaultFile.objects.create(
                client=client,
                lawyer=lawyer,
                file=uploaded_file,
                filename=uploaded_file.name
            )
            return redirect('chat_view', lawyer_id=lawyer.id)

    # Fetch messages between client and lawyer (modify this query as per your model)
    messages = Message.objects.filter(
        (models.Q(sender=client) & models.Q(receiver=lawyer)) |
        (models.Q(sender=lawyer) & models.Q(receiver=client))
    ).order_by('timestamp')

    # Get uploaded files from client to this lawyer
    vault_files = VaultFile.objects.filter(client=client, lawyer=lawyer)

    return render(request, 'chat/lawyer_chat.html', {
        'lawyer': lawyer,
        'client': client,
        'messages': messages,
        'vault_files': vault_files
    })
def chat_page(request, username):

    user = get_object_or_404(User, username=username)
    print(user, 'user')

    lawyer = get_object_or_404(LawyerDetails, id=user.id)
    print(lawyer, 'lawyer')

    client = get_object_or_404(ClientDetails, id=request.user.id)
    print(client, 'client')

    appointment = Appointment.objects.filter(user=request.user, lawyer=lawyer, status='Paid').first()
    print(appointment, 'appointment')

    if appointment:
        # Check if the client has made the payment for this appointment
        payment = Payment.objects.filter(user=request.user, lawyer=lawyer, appointment=appointment, paid=True).first()

        if payment:
            # Fetch all messages exchanged between the client and lawyer, ordered by timestamp
            messages = Message.objects.filter(client=client, lawyer=lawyer).order_by('timestamp')
            print(messages, 'messages')
        else:
            messages = None
    else:
        messages = None

    # Render the chat page with the lawyer and messages
    return render(request, 'client/chat_page.html', {'lawyer': lawyer, 'messages': messages})
    

@login_required
def client_chat(request, lawyer_id):
    # Fetch the client and lawyer objects
    client = get_object_or_404(ClientDetails, id=request.user.id)  # Access ClientDetails based on logged-in user
    lawyer = get_object_or_404(LawyerDetails, id=lawyer_id)

    # Fetch the messages between the client and the lawyer
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=lawyer.id)) | (Q(sender=lawyer.id) & Q(receiver=request.user))
    ).order_by('timestamp')

    # If the form is submitted, send the message
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text.strip():  # Ensure the message is not empty
            # Create a new message
            Message.objects.create(
                sender=request.user,  # The client is sending the message
                receiver=lawyer.id,  # The lawyer is the receiver (user object directly)
                message=message_text,
                client=client,
                lawyer=lawyer,
                timestamp=datetime.now()  # Timestamp when the message is sent
            )
            # Correct the redirection URL with lawyer.id.id (primary key of LawyerDetails)
            return redirect('client:client_chat', lawyer_id=lawyer.id.id)  # Use the actual primary key

    return render(request, 'client/chat_page.html', {
        'client': client,
        'lawyer': lawyer,
        'messages': messages,
    })

@login_required
def start_video_call(request, lawyer_id):
    # Import your User model properly
    lawyer = User.objects.get(id=lawyer_id)
    client = request.user

    # Generate random room code
    room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Create a video call room
    room = VideoCallRoom.objects.create(
        room_id=room_code,
        lawyer=lawyer,
        client=client
    )

    return redirect('client:join_video_call', room_code=room_code)


# 2. To show the Join Page
@login_required
def join_video_call(request, room_code):
    try:
        room = VideoCallRoom.objects.get(room_id=room_code)

        # Security: Only Lawyer or Client can join
        if request.user != room.client and request.user != room.lawyer:
            messages.error(request, "You are not authorized to join this call.")
            return redirect('home')

        return render(request, 'client/join_video_call.html', {'room': room})

    except VideoCallRoom.DoesNotExist:
        messages.error(request, "Call room does not exist.")
        return redirect('home')
    
@login_required
def video_call_room(request, room_code):
    try:
        room = VideoCallRoom.objects.get(room_id=room_code)

        # Security: Only client or lawyer can enter
        if request.user != room.client and request.user != room.lawyer:
            from django.contrib import messages
            messages.error(request, "You are not authorized to enter this call.")
            return redirect('home')

        return render(request, 'client/video_call_room.html', {'room': room})

    except VideoCallRoom.DoesNotExist:
        from django.contrib import messages
        messages.error(request, "Room does not exist.")
        return redirect('home')

    
def send_room_code_email(request, room_id):
    room = get_object_or_404(VideoCallRoom, room_id=room_id)

    if room.lawyer.email:
        print(room.lawyer.email)
  # Make sure the lawyer has an email
        # Send the room code via email to the lawyer
        send_mail(
            'Your Video Call Room Code',
            f'Hello {room.lawyer.first_name},\n\nYour video call room code is: {room.room_id}\n\nBest regards, Your Team.',
            settings.DEFAULT_FROM_EMAIL,
            [room.lawyer.email],
            fail_silently=False,
        )
        return HttpResponse('<script>alert("Email sent successfully!."); window.location.href ;</script>')
  
    else:
        return HttpResponse('Lawyer does not have an email address.')
    


from django.db.models import Q

@login_required
def vaultopen(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        lawyer_id = request.POST.get('lawyer')
        lawyer = User.objects.get(id=lawyer_id) if lawyer_id else None

        if file:
            VaultFile.objects.create(
                client=request.user,
                lawyer=lawyer,
                file=file,
                filename=file.name
            )
            return redirect('client:vaultopen')

    # Get lawyers whom this client has paid appointments with
    paid_appointments = Appointment.objects.filter(user=request.user, status='Paid')
    paid_lawyers = User.objects.filter(id__in=paid_appointments.values_list('lawyer__id', flat=True))

    user_files = VaultFile.objects.filter(client=request.user)

    return render(request, 'client/vaultopen.html', {
        'files': user_files,
        'lawyers': paid_lawyers
    })


@login_required
def client_profile(request):
    client = ClientDetails.objects.get(id=request.user)

    if request.method == 'POST':
        client.first_name = request.POST.get('first_name')
        client.last_name = request.POST.get('last_name')
        client.phone = request.POST.get('phone')
        client.email = request.POST.get('email')
        client.address = request.POST.get('address')
        
        if 'photo' in request.FILES:
            client.photo = request.FILES['photo']

        client.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('client:profile')

    return render(request, 'client/clientprofile.html', {'client': client})



def payments_view(request):
    user = request.user
    paid_payments = Payment.objects.filter(user=user, paid=True).select_related('lawyer', 'appointment')
    return render(request, 'client/paidview.html', {'payments': paid_payments})


def download_invoice(request, payment_id):
    try:
        payment = Payment.objects.select_related('appointment', 'lawyer').get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return HttpResponse("Invoice not found", status=404)

    template_path = 'client/invoice.html'
    context = {'payment': payment}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{payment.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response


@login_required
def viewstatus(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'client/view_status.html', {'appointments': appointments})


