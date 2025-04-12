from django.contrib import admin

# Register your models here.
from .models import UserProfile, Event

# admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(Event)