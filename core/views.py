from .models import CustomUser  
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings
from datetime import date, timedelta,  datetime
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
import io
import uuid

def generate_invoice(request, context_data):
    template_path = 'invoice.html'
    context = context_data

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="GymGenie_Invoice.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('UTF-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

PLANS = {
    'basic': {'duration_days': 30, 'price': 199},
    'premium': {'duration_days': 90, 'price': 499},
    'pro': {'duration_days': 180, 'price': 899},
}

@login_required
def join_plan(request, plan_name):
    if plan_name not in PLANS:
        messages.error(request, "Invalid plan selected.")
        return redirect('home')
    request.session['selected_plan'] = plan_name
    return redirect('payment')

@login_required
def payment(request):
    plan_key = request.session.get('selected_plan')
    if not plan_key or plan_key not in PLANS:
        messages.error(request, "Invalid plan.")
        return redirect('home')

    plan = PLANS[plan_key]
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Razorpay needs price in paise
    amount_in_paise = plan['price'] * 100

    # Create Razorpay Order
    razorpay_order = client.order.create(dict(
        amount=amount_in_paise,
        currency='INR',
        payment_capture='1'
    ))

    request.session['razorpay_order_id'] = razorpay_order['id']

    context = {
        'plan_key': plan_key,
        'plan_name': plan_key.title(),
        'plan_price': plan['price'],
        'plan_duration': plan['duration_days'],
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'amount': amount_in_paise,
        'currency': 'INR',
        'callback_url': '/payment/success/'
    }
    return render(request, 'payment.html', context)

# Handle success
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
def payment_success(request):
    plan_key = request.session.get('selected_plan')
    if not plan_key or plan_key not in PLANS:
        messages.error(request, "Invalid plan.")
        return redirect('home')

    plan = PLANS[plan_key]
    user = request.user
    today = date.today()
    current_valid = user.valid_until if user.valid_until and user.valid_until > today else today
    user.valid_until = current_valid + timedelta(days=plan['duration_days'])
    user.save()

    today = datetime.now().strftime('%Y%m%d')  # Gives '20240527'
    unique_suffix = str(uuid.uuid4()).split('-')[0].upper()[:6]  # Short unique code like 'ABC123'
    invoice_id = f"GYM-{today}-{unique_suffix}"
    invoice_date = datetime.now().strftime('%d-%m-%Y')  # Format like: 28-05-2025
    context = {
        'user': user,
        'plan_name': plan_key.title(),
        'plan_price': plan['price'],
        'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'valid_until': user.valid_until,
        'invoice_id': invoice_id,
        'invoice_date': invoice_date,
        'logo_url': request.build_absolute_uri('/static/logo.png')  # Place your logo in static/
    }

    del request.session['selected_plan']
    return generate_invoice(request, context)



def home(request):
    return render(request, 'base.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Redirect to dashboard
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        age = request.POST['age']
        gender = request.POST['gender']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        # Create user with extra fields
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.age = age
        user.gender = gender
        user.save()

        messages.success(request, "Signup successful! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


def weight_gain(request):
    return render(request, 'weight_gain.html')

from .models import Progress
from .forms import ProgressForm
from django.utils.timezone import is_naive

@login_required
def track_progress(request):
    user = request.user
    if request.method == 'POST':
        form = ProgressForm(request.POST, request.FILES)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.user = user
            progress.save()
    else:
        form = ProgressForm()

    progress_entries = Progress.objects.filter(user=user).exclude(date=None).order_by('-date')

    # Optional Debug
    for entry in progress_entries:
        if not isinstance(entry.date, datetime):
            print(f"Invalid date format: {entry.date} ({type(entry.date)})")

    return render(request, 'track_progress.html', {
        'form': form,
        'progress_entries': progress_entries,
    })

