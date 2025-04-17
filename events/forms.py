from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Event, UserProfile

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Event date'
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text='Event time'
    )
    
    sale_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Ticket sale start date'
    )   
    sale_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Ticket sale end date'
    )
    
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'capacity', 'status', 'ticket_type', 'ticket_price', 'sale_start_date', 'sale_end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'ticket_type': forms.Select(attrs={'class': 'form-select'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        def __init__(self, *args, **kwargs):
            super(EventForm, self).__init__(*args, **kwargs)

            # Initially set fields as not required
            self.fields['ticket_price'].required = False
            self.fields['sale_start_date'].required = False
            self.fields['sale_end_date'].required = False

            # Dynamically adjust based on ticket type (must be called inside __init__)
            if self.data.get('ticket_type') == 'paid':
                self.fields['ticket_price'].required = True
                self.fields['sale_start_date'].required = True
                self.fields['sale_end_date'].required = True

   
    def clean_date(self):
        import datetime
        date_val = self.cleaned_data.get('date')
        today = datetime.date.today()
        if date_val < today:
            raise forms.ValidationError("Event date cannot be in the past")
        return date_val
    
    def clean(self):
        cleaned_data = super().clean()  # Always call super().clean()
        from datetime import date,datetime, timedelta
        from django.utils import timezone
        ticket_type = cleaned_data.get('ticket_type')
        event_date = cleaned_data.get('date')
        # event_time = cleaned_data.get('time')
        today = date.today()
        # --- VENUE Booking Check ---
        location = cleaned_data.get('location')
        time = cleaned_data.get('time')
        status = cleaned_data.get('status')
        
        # Only check venue availability if the status is being set to "published"
        if status == 'published' and location and date and time:
            # For edit form, we need to exclude the current event ID
            instance_id = self.instance.id if self.instance and self.instance.pk else None
            
            if not Event.check_venue_availability(location, event_date, time, exclude_id=instance_id):
                self.add_error('location', 'This venue is already booked at the selected date and time.')
                self.add_error('date', 'Please select a different date or time for this venue.')
                self.add_error('time', 'Please select a different time slot for this venue.')
             

        # --- Paid Ticket Validations ---
        if ticket_type == 'paid':
            ticket_price = cleaned_data.get('ticket_price')
            sale_start_date = cleaned_data.get('sale_start_date')
            sale_end_date = cleaned_data.get('sale_end_date')

            if not ticket_price:
                raise forms.ValidationError('Ticket price is required for paid events.')
            if not sale_start_date:
                raise forms.ValidationError('Sale start date is required for paid events.')
            if not sale_end_date:
                raise forms.ValidationError('Sale end date is required for paid events.')

            if sale_start_date and sale_end_date and event_date:
                if sale_start_date > sale_end_date:
                    raise forms.ValidationError('Sale end date must be after sale start date.')
                if sale_start_date < today or sale_end_date < today:
                    raise forms.ValidationError("Sale dates cannot be in the past")
                if sale_start_date > event_date or sale_end_date > event_date:
                    raise forms.ValidationError("Sale dates cannot be after the event date")

        return cleaned_data

# class RegisterForm(forms.ModelForm):
    
