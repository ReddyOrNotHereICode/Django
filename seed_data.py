from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from jobs.models import Job, Application
import os

# Create groups
applicant_group, _ = Group.objects.get_or_create(name='applicant')
recruiter_group, _ = Group.objects.get_or_create(name='recruiter')

User = get_user_model()

# Get passwords from environment or use a secure default
applicant_password = os.environ.get('SEED_APPLICANT_PASSWORD', 'testpass123')
recruiter_password = os.environ.get('SEED_RECRUITER_PASSWORD', 'testpass123')

# Create sample users
if not User.objects.filter(username='applicant1').exists():
     applicant1 = User.objects.create(
         username='applicant1',
         email='applicant1@example.com',
         password=make_password(applicant_password)
     )
     applicant1.groups.add(applicant_group)
else:
    applicant1 = User.objects.get(username='applicant1')

if not User.objects.filter(username='recruiter1').exists():
    recruiter1 = User.objects.create(
        username='recruiter1',
        email='recruiter1@example.com',
        password=make_password(recruiter_password)
    )
    recruiter1.groups.add(recruiter_group)
else:
    recruiter1 = User.objects.get(username='recruiter1')

# Create sample jobs
if not Job.objects.filter(title='Sample Job 1').exists():
    job1 = Job.objects.create(
        employer=recruiter1,
        title='Sample Job 1',
        description='This is a sample job description for Job 1.',
        location='Remote'
    )
else:
    job1 = Job.objects.get(title='Sample Job 1')

if not Job.objects.filter(title='Sample Job 2').exists():
    job2 = Job.objects.create(
        employer=recruiter1,
        title='Sample Job 2',
        description='This is a sample job description for Job 2.',
        location='New York'
    )
else:
    job2 = Job.objects.get(title='Sample Job 2')

# Create sample application
if not Application.objects.filter(applicant=applicant1, job=job1).exists():
    Application.objects.create(
        job=job1,
        applicant=applicant1,
        cover_letter='I am interested in Sample Job 1.'
    )
