from django.urls import path
from .views import login_view, event_list_view

urlpatterns = [
    path('', login_view, name='login'),  # Uncomment this line
    path('events/', event_list_view, name='event_list'),
]
