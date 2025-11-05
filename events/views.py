from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Event, Attendee
from .forms import AttendeeRegistrationForm, AttendeeSearchForm, CheckInForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import CustomUser
from django.contrib import messages # Import messages for success/error feedback
from django.contrib.auth.decorators import login_required

# Public views for attendees
def event_list(request):
    events = Event.objects.filter(is_active=True, registration_open=True).order_by('start_date')
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    return render(request, 'events/event_detail.html', {'event': event})

def register_attendee(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True, registration_open=True)
    
    # Check if event is full
    if event.is_full():
        messages.error(request, "Sorry, this event is fully booked. No more registrations can be accepted.")
        return redirect('events:event_detail', event_id=event_id)
    
    # Check if there's only 1 spot left (for warning message)
    is_last_spot = event.available_spots() == 1
    
    if request.method == 'POST':
        form = AttendeeRegistrationForm(request.POST, event=event)
        if form.is_valid():
            # Double-check capacity before saving (race condition protection)
            if event.is_full():
                messages.error(request, "Sorry, this event just became fully booked. Please try another event.")
                return redirect('events:event_detail', event_id=event_id)
            
            try:
                with transaction.atomic():
                    attendee = form.save(commit=False)
                    attendee.event = event
                    
                    # Handle user account creation
                    create_account = form.cleaned_data.get('create_account', False)
                    if create_account and not request.user.is_authenticated:
                        username = form.cleaned_data['username']
                        password = form.cleaned_data['password']
                        email = form.cleaned_data['email']
                        
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name']
                        )
                        attendee.user = user
                        login(request, user)
                    
                    elif request.user.is_authenticated:
                        attendee.user = request.user
                    
                    attendee.save()
                    
                    messages.success(request, f"Successfully registered for {event.title}!")
                    if is_last_spot:
                        messages.info(request, "You got the last available spot!")
                    
                    return redirect('events:registration_confirmation', confirmation_code=attendee.confirmation_code)
                    
            except Exception as e:
                messages.error(request, "An error occurred during registration. Please try again.")
                print(f"Registration error: {e}")
    
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data.update({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            })
        form = AttendeeRegistrationForm(initial=initial_data, event=event)
    
    return render(request, 'events/register_attendee.html', {
        'form': form, 
        'event': event,
        'available_spots': event.available_spots(),
        'is_last_spot': is_last_spot
    })

def registration_confirmation(request, confirmation_code):
    attendee = get_object_or_404(Attendee, confirmation_code=confirmation_code)
    return render(request, 'events/registration_confirmation.html', {'attendee': attendee})

@login_required
def my_registrations(request):
    attendee_registrations = Attendee.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).select_related('event').order_by('-registration_date')
    
    return render(request, 'events/my_registrations.html', {
        'registrations': attendee_registrations
    })

def check_registration_status(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        confirmation_code = request.POST.get('confirmation_code')
        
        try:
            attendee = Attendee.objects.get(email=email, confirmation_code=confirmation_code)
            return render(request, 'events/registration_status.html', {'attendee': attendee})
        except Attendee.DoesNotExist:
            messages.error(request, "No registration found with the provided details.")
    
    return render(request, 'events/check_registration.html')

# Management views for event managers
def is_event_manager(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_event_manager)
def manage_attendees(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, id=event_id)
        attendees = event.attendees.all()
    else:
        event = None
        attendees = Attendee.objects.all()
    
    form = AttendeeSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        
        if search:
            attendees = attendees.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(confirmation_code__icontains=search)
            )
        if category:
            attendees = attendees.filter(category=category)
    
    stats = {
        'total': attendees.count(),
        'checked_in': attendees.filter(attendance_status='checked_in').count(),
        'registered': attendees.filter(attendance_status='registered').count(),
        'cancelled': attendees.filter(attendance_status='cancelled').count(),
    }
    
    return render(request, 'events/manage_attendees.html', {
        'event': event,
        'attendees': attendees,
        'form': form,
        'stats': stats
    })

@login_required
@user_passes_test(is_event_manager)
def check_in_attendee(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            confirmation_code = form.cleaned_data['confirmation_code'].upper()
            
            try:
                attendee = Attendee.objects.get(
                    event=event, 
                    confirmation_code=confirmation_code
                )
                
                if attendee.attendance_status == 'checked_in':
                    messages.warning(request, f"{attendee.full_name} is already checked in.")
                elif attendee.attendance_status == 'cancelled':
                    messages.error(request, f"{attendee.full_name} registration is cancelled.")
                else:
                    attendee.attendance_status = 'checked_in'
                    attendee.check_in_time = timezone.now()
                    attendee.save()
                    messages.success(request, f"Successfully checked in {attendee.full_name}!")
                
                return redirect('events:check_in_attendee', event_id=event_id)
                
            except Attendee.DoesNotExist:
                messages.error(request, "No attendee found with this confirmation code.")
    
    else:
        form = CheckInForm()
    
    # Get recent check-ins
    recent_checkins = event.attendees.filter(
        attendance_status='checked_in'
    ).order_by('-check_in_time')[:10]
    
    return render(request, 'events/check_in.html', {
        'event': event,
        'form': form,
        'recent_checkins': recent_checkins
    })

@login_required
@user_passes_test(is_event_manager)
def update_attendance_status(request, attendee_id):
    if request.method == 'POST':
        attendee = get_object_or_404(Attendee, id=attendee_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Attendee.ATTENDANCE_STATUS):
            attendee.attendance_status = new_status
            if new_status == 'checked_in' and not attendee.check_in_time:
                attendee.check_in_time = timezone.now()
            attendee.save()
            messages.success(request, f"Updated {attendee.full_name} status to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
    
    return redirect('events:manage_attendees', event_id=attendee.event.id)

@login_required
@user_passes_test(is_event_manager)
def attendance_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendees = event.attendees.all()
    
    status_counts = {
        'checked_in': attendees.filter(attendance_status='checked_in').count(),
        'registered': attendees.filter(attendance_status='registered').count(),
        'cancelled': attendees.filter(attendance_status='cancelled').count(),
        'no_show': attendees.filter(attendance_status='no_show').count(),
    }
    
    return render(request, 'events/attendance_report.html', {
        'event': event,
        'attendees': attendees,
        'status_counts': status_counts
    })

def check_registration_api(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.user.is_authenticated:
        is_registered = Attendee.objects.filter(
            event=event,
        ).filter(
            Q(user=request.user) | Q(email=request.user.email)
        ).exists()
    else:
        is_registered = False
    
    return JsonResponse({
        'is_registered': is_registered,
        'total_registered': event.registered_attendees_count(),
        'max_attendees': event.max_attendees,
        'spots_remaining': event.max_attendees - event.registered_attendees_count()
    })

# This is the login view
User = get_user_model()               # ✅ This will point to Event_App.CustomUser

def login_view(request):
   # if request.user.is_authenticated:
   #     return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Checkbox value

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'Event_App/login.html', {
                'error': 'Invalid email or password.'
            })

        if user.check_password(password):
            login(request, user)

            # Set session expiry
            if not remember_me:
                # Session expires when browser is closed
                request.session.set_expiry(0)
            else:
                # Default: session lasts for 2 weeks (in seconds)
                request.session.set_expiry(1209600)  # 2 weeks

            return redirect('dashboard')

        else:
            return render(request, 'Event_App/login.html', {
                'error': 'Invalid email or password.'
            })

    return render(request, 'Event_App/login.html')




def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'Event_App/signup.html', {
                'error': 'Passwords do not match.'
            })

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'Event_App/signup.html', {
                'error': 'Email already taken.'
            })

        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=full_name
            )
            user.save()

            messages.success(request, 'Account created successfully! Please log in.', extra_tags='signup_success')

            return redirect('login')

        except Exception as e:
            return render(request, 'Event_App/signup.html', {
                'error': 'An error occurred during registration.'
            })

    return render(request, 'Event_App/signup.html')




def forgotpassword_view(request):
    return render(request, 'Event_App/forgotpassword.html')

@login_required
def dashboard_view(request):
    return render(request, 'Event_App/dashboard.html')

def markets_view(request):
    return render(request, 'Event_App/markets.html')