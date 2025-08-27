from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from E_lawyer.lawyer.models import *
from E_lawyer.client.models import *
from django.db.models import Sum
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa


# Create your views here.
def  HomeView(request):
    return render(request,'home/index.html')




def  LawyerHome(request):
    return render(request,'home/lawyerindex.html')


def AdminHome(request):
    client_count = ClientDetails.objects.count()
    lawyer_count = LawyerDetails.objects.count()
    total_payment = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'client_count': client_count,
        'lawyer_count': lawyer_count,
        'total_payment': total_payment,
    }

    return render(request, 'c_admin/adminindex.html', context)

def AboutView(request):
    return render(request,'home/about.html')


def dashboard(request):
    return redirect('Law:ahome')


def view_clients(request):
    clients = ClientDetails.objects.all()
    return render(request, 'c_admin/view_clients.html', {'clients': clients})

def view_lawyers(request):
    lawyers = LawyerDetails.objects.all()
    return render(request, 'c_admin/view_lawyers.html', {'lawyers': lawyers})

@csrf_exempt
def verify_lawyer(request, pk):
    if request.method == "POST":
        lawyer = get_object_or_404(LawyerDetails, pk=pk)
        if not lawyer.is_verified:
            lawyer.is_verified = True
            lawyer.save()

            # Send verification email
            send_mail(
                'Lawyer Verification Successful',
                f'Dear {lawyer.first_name},\n\nYour account has been verified by the admin. You can now fully access all features.',
                settings.EMAIL_HOST_USER,
                [lawyer.email],
                fail_silently=False,
            )

            messages.success(request, f'{lawyer.first_name} has been verified and notified via email.')
    return redirect('Law:lawyerview')


def delete_client(request, id):
    client = get_object_or_404(ClientDetails, pk=id)
    client.delete()
    messages.success(request, "Client deleted successfully.")
    return redirect('Law:clientview')

def delete_lawyer(request, id):
    if request.method == 'POST':
        lawyer = get_object_or_404(LawyerDetails, id=id)
        lawyer.delete()
        return redirect('Law:lawyerview')

    
def billview(request):
    payments = Payment.objects.select_related('user', 'lawyer', 'appointment').all()
    return render(request, 'c_admin/billview.html', {'payments': payments})



def view_appointments(request):
    appointments = Appointment.objects.all()
    return render(request, 'c_admin/view_appointments.html', {'appointments': appointments})


def download_invoice(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, paid=True)
    template_path = 'c_admin/admin_invoice.html'
    context = {'payment': payment}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{payment_id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating invoice PDF', status=500)
    return response


def logout_view(request):
    logout(request)
    return redirect('/client/login')