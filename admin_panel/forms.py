from django import forms
from accounts.models import User
from tasks.models import Task
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices, initial=User.Role.USER)
    assigned_admin = forms.ModelChoiceField(queryset=User.objects.filter(role=User.Role.ADMIN), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'assigned_admin', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email','role','assigned_admin','is_active')

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title','description','assigned_to','due_date','status','completion_report','worked_hours')
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get('status')
        report = cleaned.get('completion_report')
        hours = cleaned.get('worked_hours')
        if status == Task.STATUS_COMPLETED:
            if not report:
                self.add_error('completion_report', 'Completion report required when marking Completed.')
            if hours is None:
                self.add_error('worked_hours', 'Worked hours required when marking Completed.')
        return cleaned
