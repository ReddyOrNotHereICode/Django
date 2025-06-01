from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Job, Application, Notification
from .forms import JobForm, ApplicationForm, ApplicationStatusForm, GroupRequestForm
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

APPLICANT_GROUP = 'applicant'
RECRUITER_GROUP = 'recruiter'

# List all jobs
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    is_recruiter = False
    unread_notifications = 0
    if request.user.is_authenticated:
        is_recruiter = request.user.groups.filter(name=RECRUITER_GROUP).exists()
        unread_notifications = request.user.notifications.filter(status='unread').count()
    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'is_recruiter': is_recruiter, 'unread_notifications': unread_notifications})

# Job detail and application
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    can_apply = False
    if request.user.is_authenticated and request.user.groups.filter(name=APPLICANT_GROUP).exists():
        can_apply = True
    if request.method == 'POST':
        if not can_apply:
            return redirect('login')
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            # Notify recruiter of new application
            from jobs.models import Notification
            Notification.objects.create(
                user=job.employer,
                message=f"New application for '{job.title}' from {request.user.username}",
                url=reverse('applications')
            )
            return redirect('job_list')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/job_detail.html', {'job': job, 'form': form, 'can_apply': can_apply})

# Post a new job
@login_required
def post_job(request):
    if not request.user.groups.filter(name=RECRUITER_GROUP).exists():
        messages.error(request, 'You do not have permission to post jobs.')
        return HttpResponseForbidden('You do not have permission to post jobs.')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            return redirect('job_list')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def applications_view(request):
    user = request.user
    applications = []
    is_recruiter = user.groups.filter(name=RECRUITER_GROUP).exists()

    if is_recruiter:
        jobs = Job.objects.filter(employer=user)
        applications = Application.objects.filter(job__in=jobs).select_related('job', 'applicant').order_by('-created_at')
        if request.method == 'POST' and 'save_app' in request.POST:
            return _handle_recruiter_application_status_update(request, user)
    elif user.groups.filter(name=APPLICANT_GROUP).exists():
        applications = Application.objects.filter(applicant=user).select_related('job').order_by('-created_at')

    return render(request, 'jobs/applications.html', {
        'applications': applications,
        'is_recruiter': is_recruiter
    })

def _handle_recruiter_application_status_update(request, user):
    app_id = request.POST.get('save_app')
    try:
        app_id_int = int(app_id)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid application ID.')
        return redirect('applications')
    new_status = request.POST.get(f'status_{app_id}')
    allowed_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
    if new_status not in allowed_statuses:
        messages.error(request, 'Invalid status value.')
        return redirect('applications')
    try:
        app = Application.objects.get(id=app_id_int, job__employer=user)
    except Application.DoesNotExist:
        messages.error(request, 'Application not found or access denied.')
        return redirect('applications')
    if new_status and new_status != app.status:
        app.status = new_status
        if new_status != 'pending':
            app.processed_at = timezone.now()
            Notification.objects.create(
                user=app.applicant,
                message=f"Your application for '{app.job.title}' was {new_status}.",
                url=reverse('applications')
            )
        app.save()
    return redirect('applications')

@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-created_at')
    if request.method == 'POST':
        notif_id = request.POST.get('notif_id')
        action = request.POST.get('action')
        notif = get_object_or_404(Notification, id=notif_id, user=request.user)
        if action == 'mark_read' or action == 'restore':
            notif.status = 'read'
            notif.save()
        elif action == 'mark_unread':
            notif.status = 'unread'
            notif.save()
        elif action == 'delete':
            notif.status = 'deleted'
            notif.save()
        return redirect('notifications')
    return render(request, 'jobs/notifications.html', {'notifications': notifications})

@login_required
def group_request_view(request):
    if request.method == 'POST':
        form = GroupRequestForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            message = form.cleaned_data['message']
            # Notify all superusers
            for admin in User.objects.filter(is_superuser=True):
                Notification.objects.create(
                    user=admin,
                    message=f"New group request: {request.user.username} requests {group} - {message}",
                    url=reverse('admin:auth_user_change', args=[request.user.id])
                )
            messages.success(request, 'Your request has been sent to the admins.')
            return redirect('group_request')
    else:
        form = GroupRequestForm()
    return render(request, 'jobs/group_request.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def admin_group_requests_view(request):
    # Show all notifications for group requests
    notifications = Notification.objects.filter(user=request.user, message__startswith='New group request:').order_by('-created_at')
    return render(request, 'jobs/admin_group_requests.html', {'notifications': notifications})
