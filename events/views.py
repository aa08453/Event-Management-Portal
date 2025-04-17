from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Event, UserProfile, Registration
from .forms import EventForm, CustomLoginForm

def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    # Get the current user and their profile
    user = request.user
    try:
        user_profile = user.profile
        is_event_manager = user_profile.user_type == 'event_manager'
        is_student = user_profile.user_type == 'student'
    except UserProfile.DoesNotExist:
        is_event_manager = False
        is_student = False

    # Base queryset for events
    events = Event.objects.filter(status='published').order_by('-created_at')

    # Filters for students
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    selected_date = request.GET.get('date', '')
    selected_ticket_type = request.GET.get('ticket_type', '')

    if query:
        events = events.filter(name__icontains=query)
    if location:
        events = events.filter(location=location)
    if selected_date:
        try:
            date_obj = timezone.datetime.strptime(selected_date, "%Y-%m-%d").date()
            events = events.filter(date=date_obj)
        except (ValueError, TypeError):
            pass
    if selected_ticket_type:
        events = events.filter(ticket_type=selected_ticket_type)
        
    total_events = 0
    published_count = 0
    upcoming_count = 0
    user_registrations = []
    user_registered_events = []
    
    if is_event_manager:
        events = Event.objects.filter(organizer=user).order_by('-created_at')
        total_events = events.count()
        published_count = events.filter(status='published').count()
        upcoming_count = events.filter(date__gte=timezone.now().date(), status='published').count()
    
    elif is_student:
        user_registrations = Registration.objects.filter(user=user).select_related('event').order_by('event__date')
        user_registered_events = [reg.event for reg in user_registrations]

    context = {
        'events': events,
        'total_events': total_events,
        'published_count': published_count,
        'upcoming_count': upcoming_count,
        'is_event_manager': is_event_manager,
        'is_student': is_student,
        'query': query,
        'location_choices': Event.LOCATION_CHOICES,
        'selected_location': location,
        'selected_date': selected_date,
        'selected_ticket_type': selected_ticket_type,
    }
    
    # Add student-specific context
    if is_student:
        context.update({
            'user_registrations': user_registrations,
            'user_registered_events': user_registered_events,
        })

    return render(request, 'dashboard.html', context)

@login_required
def create_event(request):
    user = request.user
    
    try:
        user_profile = user.profile
        if user_profile.user_type != 'event_manager':
            messages.error(request, "Only event managers can create events.")
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, "You don't have permission to create events.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = user
            event.save()
            messages.success(request, f"Event '{event.name}' has been created successfully!")
            return redirect('dashboard')
        else:
            # If the form is invalid, print the errors
            print(form.errors)
            # You can also use this to pass the errors to the template
            

    else:
        form = EventForm()
    
    return render(request, 'create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    user = request.user
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is the organizer of this event
    if event.organizer != user:
        messages.error(request, "You don't have permission to edit this event.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.name}' has been updated successfully!")
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    user = request.user
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is the organizer of this event
    if event.organizer != user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': "You don't have permission to delete this event."})
        messages.error(request, "You don't have permission to delete this event.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"Event '{event_name}' has been deleted successfully!"})
            
        messages.success(request, f"Event '{event_name}' has been deleted successfully!")
        return redirect('dashboard')
    
    return render(request, 'delete_event.html', {'event': event})

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, status='published')
    
    if request.user.profile.user_type != 'student':
        messages.error(request, "Only students can register for events.")
        return redirect('dashboard')
    
    # Check if user is already registered
    already_registered = Registration.objects.filter(user=request.user, event=event).exists()
 
    if request.method == 'POST':
        # Check if the event is published and not in the past
        if event.is_past_event:
            messages.error(request, "This event has already occurred and cannot be registered for.")
            return redirect('dashboard')
            
        # Check if event is at capacity
        if event.is_full:
            messages.error(request, "Sorry, this event has reached its maximum capacity.")
            return redirect('dashboard')

        # Check if the user is already registered for the event
        if already_registered:
            messages.warning(request, "You are already registered for this event.")
            return redirect('dashboard')
            
        # For paid events, check if sales are open
        if event.ticket_type == 'paid':
            today = timezone.now().date()
            if not (event.sale_start_date <= today <= event.sale_end_date):
                messages.error(request, "Ticket sales for this event are not currently open.")
                return redirect('dashboard')

        Registration.objects.create(user=request.user, event=event)
        messages.success(request, f"You have successfully registered for '{event.name}'!")
        return redirect('dashboard')

    context = {
        'event': event,
        'already_registered': already_registered,
    }

    return render(request, 'register_event.html', context)



    