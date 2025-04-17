from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('event_manager', 'Event Manager'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='student')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    LOCATION_CHOICES = (
        ('audi','H.M. AUDITORIUM'),
        ('soorty','SOORTY'),
        ('tariq_rafi','TARIQ RAFI'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200, choices=LOCATION_CHOICES, default = 'audi')
    capacity = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    TICKET_TYPE_CHOICES = (
        ('free', 'Free'),
        ('paid', 'Paid'),
    )
    
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPE_CHOICES, default='free')
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sale_start_date = models.DateField(null=True, blank=True)
    sale_end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_past_event(self):
        event_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return event_datetime < timezone.now()
    
    @property
    def remaining_capacity(self):
        registered_count = self.registrations.count()
        return max(0, self.capacity - registered_count)
    
    @property
    def is_full(self):
        return self.remaining_capacity <= 0
    
    @classmethod
    def check_venue_availability(cls, location, date, time, exclude_id=None):
        """
        Check if the venue is already booked for a given date and time
        Returns True if the venue is available, False otherwise
        """
        # Convert time to a datetime.time object if it's a string
        if isinstance(time, str):
            import datetime
            hour, minute = map(int, time.split(':'))
            time = datetime.time(hour, minute)
            
        # Check for any events at the same location, date, and approximate time
        # (within a 2-hour window)
        import datetime
        
        # Calculate 2 hours before and after the given time
        start_time = datetime.datetime.combine(datetime.date.today(), time) - datetime.timedelta(hours=2)
        end_time = datetime.datetime.combine(datetime.date.today(), time) + datetime.timedelta(hours=2)
        
        query = cls.objects.filter(
            location=location,
            date=date,
            status='published'  # Only published events block venue
        )
        
        # Exclude the current event if editing
        if exclude_id:
            query = query.exclude(id=exclude_id)
            
        # Check if any event exists in the time range
        for event in query:
            event_time = datetime.datetime.combine(datetime.date.today(), event.time)
            if start_time.time() <= event_time.time() <= end_time.time():
                return False
                
        return True

class Registration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    
    class Meta:
        unique_together = ('user', 'event')
        
    def __str__(self):
        return f"{self.user.username} - {self.event.name}"