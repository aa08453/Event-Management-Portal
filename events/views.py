from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Event, UserProfile
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
    user = request.user
    
    try:
        user_profile = user.profile
        is_event_manager = user_profile.user_type == 'event_manager'
    except UserProfile.DoesNotExist:
        is_event_manager = False
    
    if is_event_manager:
        events = Event.objects.filter(organizer=user).order_by('-created_at')
        published_count = events.filter(status='published').count()
        upcoming_count = events.filter(date__gte=timezone.now().date(), status='published').count()
    else:
        events = Event.objects.filter(status='published').order_by('-created_at')
        published_count = events.count()
        upcoming_count = events.filter(date__gte=timezone.now().date()).count()
    
    context = {
        'events': events,
        'total_events': events.count(),
        'published_count': published_count,
        'upcoming_count': upcoming_count,
        'is_event_manager': is_event_manager
    }
    
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
