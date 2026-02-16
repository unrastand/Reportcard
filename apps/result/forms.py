from django import forms
from django.forms import modelformset_factory

from .models import Result, Attendance
from apps.students.models import Student
from apps.academics.models import Subject, Semester


class TeacherResultForm(forms.ModelForm):
    """ Form for teachers to enter student marks """
    student_name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False
    )
    
    class Meta:
        model = Result
        fields = ['student', 'semester', 'subject', 'practical_marks', 'theory_marks']
        widgets = {
            'student': forms.HiddenInput(),
            'semester': forms.HiddenInput(),
            'subject': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.student:
            self.fields['student_name'].initial = self.instance.student.admission_student.name


class TeacherAttendanceForm(forms.ModelForm):
    """ Form for teachers to mark student attendance """
    student_name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False
    )
    
    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'semester', 'date', 'status']
        widgets = {
            'student': forms.HiddenInput(),
            'subject': forms.HiddenInput(),
            'semester': forms.HiddenInput(),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.student:
            self.fields['student_name'].initial = self.instance.student.admission_student.name


class TeacherMarkEntryForm(forms.Form):
    """ Form for bulk mark entry by teachers """
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class TeacherAttendanceEntryForm(forms.Form):
    """ Form for bulk attendance entry by teachers """
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


# Formset for bulk mark entry
ResultFormSet = modelformset_factory(
    Result,
    form=TeacherResultForm,
    fields=['student', 'semester', 'subject', 'practical_marks', 'theory_marks'],
    extra=0,
    can_delete=False
)

# Formset for bulk attendance entry
AttendanceFormSet = modelformset_factory(
    Attendance,
    form=TeacherAttendanceForm,
    fields=['student', 'subject', 'semester', 'date', 'status'],
    extra=0,
    can_delete=False
)