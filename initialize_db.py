import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management_portal.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile, Event
from django.utils import timezone
import datetime

def create_sample_data():
    # Create departments
    # departments = [
    #     Department.objects.create(name='Computer Science'),
    #     Department.objects.create(name='Business School'),
    #     Department.objects.create(name='Engineering'),
    #     Department.objects.create(name='Arts & Humanities')
    # ]
    
    # Create event manager
    if not User.objects.filter(username='manager1').exists():
        manager = User.objects.create_user(
            username='manager1',
            email='manager1@university.edu',
            password='password',
            first_name='John',
            last_name='Doe'
        )
        UserProfile.objects.create(
            user=manager,
            user_type='event_manager',
            # department=departments[0]
        )
        
        # Create another event manager
        manager2 = User.objects.create_user(
            username='manager2',
            email='manager2@university.edu',
            password='password',
            first_name='Jane',
            last_name='Smith'
        )
        UserProfile.objects.create(
            user=manager2,
            user_type='event_manager',
            # department=departments[1]
        )
    
    # Create student
    if not User.objects.filter(username='student1').exists():
        student = User.objects.create_user(
            username='student1',
            email='student1@university.edu',
            password='password',
            first_name='Alex',
            last_name='Johnson'
        )
        UserProfile.objects.create(
            user=student,
            user_type='student',
        )
        
    if not User.objects.filter(username='student2').exists():
        student = User.objects.create_user(
            username='student2',
            email='student2@university.edu',
            password='password',
            first_name='James',
            last_name='Smith'
        )
        UserProfile.objects.create(
            user=student,
            user_type='student',
        )
    
    # Create events
    manager = User.objects.get(username='manager1')
    
    if Event.objects.count() == 0:
        # Sample events for the first manager
        today = timezone.now().date()
        
        Event.objects.create(
            name='Introduction to AI Workshop',
            description='Learn the basics of artificial intelligence and machine learning in this hands-on workshop.',
            date=today + datetime.timedelta(days=7),
            time=datetime.time(14, 0),  # 2:00 PM
            location='Arif Habib Classroom, E 109',
            capacity=50,
            status='published',
            organizer=manager
        )
        
        Event.objects.create(
            name='Web Development Hackathon',
            description='A 48-hour hackathon to build innovative web applications.',
            date=today + datetime.timedelta(days=14),
            time=datetime.time(9, 0),  # 9:00 AM
            location='Engineering Center, Main Hall',
            capacity=100,
            status='published',
            organizer=manager
        )
        
        Event.objects.create(
            name='Career Fair: Tech Industry',
            description='Meet representatives from leading tech companies and explore job opportunities.',
            date=today + datetime.timedelta(days=21),
            time=datetime.time(10, 0),  # 10:00 AM
            location='University Center, Grand Ballroom',
            capacity=200,
            status='draft',
            organizer=manager
        )
        
        # Sample events for the second manager
        manager2 = User.objects.get(username='manager2')
        
        Event.objects.create(
            name='Business Leadership Conference',
            description='A conference featuring speakers from Fortune 500 companies discussing leadership strategies.',
            date=today + datetime.timedelta(days=10),
            time=datetime.time(13, 0),  # 1:00 PM
            location='Business School Auditorium',
            capacity=150,
            status='published',
            organizer=manager2
        )
        
        Event.objects.create(
            name='Entrepreneurship Workshop',
            description='Learn how to start and grow your own business from successful entrepreneurs.',
            date=today + datetime.timedelta(days=5),
            time=datetime.time(15, 30),  # 3:30 PM
            location='Innovation Hub, Room 203',
            capacity=75,
            status='published',
            organizer=manager2
        )

if __name__ == '__main__':
    create_sample_data()
    print('Sample data has been created successfully!')