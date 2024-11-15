from django import forms
from teenApp.entities.task import Task
from teenApp.entities.child import Child
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django import forms
from teenApp.entities.task import Task
from teenApp.entities.child import Child

from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='תאריך התחלה')
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='תאריך סיום')

class CreateUserForm(UserCreationForm):
    captcha = CaptchaField()
    phone = forms.CharField(max_length=10, required=False, help_text='Enter a valid phone number.')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user

class TaskImageForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['img']

class IdentifyChildForm(forms.Form):
    identifier = forms.CharField(max_length=5, label='מספר מזהה')
    secret_code = forms.CharField(max_length=3, label='קוד סודי', widget=forms.PasswordInput())

class RedemptionForm(forms.Form):
    points = forms.IntegerField(label='Points to Redeem', min_value=1)

class BonusPointsForm(forms.Form):
    task = forms.ModelChoiceField(queryset=Task.objects.none(), label="Select Task")
    child = forms.ModelChoiceField(queryset=Child.objects.none(), label="Select Child")
    bonus_points = forms.IntegerField(label="Bonus Points", min_value=1, max_value=10)

    def __init__(self, mentor=None, *args, **kwargs):
        super(BonusPointsForm, self).__init__(*args, **kwargs)
        if mentor:
            self.fields['task'].queryset = Task.objects.filter(assigned_mentors=mentor)
            self.fields['child'].queryset = Child.objects.filter(mentors=mentor)
            


class TaskForm(forms.ModelForm):
    assigned_children = forms.ModelMultipleChoiceField(
        queryset=Child.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'points', 'deadline', 'img', 'additional_details', 'assigned_children']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'img': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'additional_details': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.mentor = kwargs.pop('mentor', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if self.mentor:
            self.fields['assigned_children'].queryset = self.mentor.children.all()



class DateRangeMForm(forms.Form):
    month = forms.DateField(widget=forms.DateInput(attrs={'type': 'month'}), label='Month')            