from django import forms
from .models import Job, Application, Notification

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']

class GroupRequestForm(forms.Form):
    group = forms.ChoiceField(choices=[('applicant', 'Applicant'), ('recruiter', 'Recruiter')])
    message = forms.CharField(widget=forms.Textarea, label='Reason for request')
