from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.forms import modelformset_factory
from django.db.models import Q

from apps.students.models import Student
from apps.academics.models import Semester, Subject, Department
from .models import Result, SubjectGroup, Attendance
from .filters import ResultFilter, SubjectGroupFilter
from .forms import (
    TeacherResultForm, TeacherAttendanceForm, 
    TeacherMarkEntryForm, TeacherAttendanceEntryForm,
    ResultFormSet, AttendanceFormSet
)
from permission_handlers.basic import user_is_verified, user_is_teacher
from permission_handlers.administrative import user_is_teacher_or_administrative


@user_passes_test(user_is_verified)
def result_view(request):
    if not request.GET:
        qs = Result.objects.none()
    else:
        qs = Result.objects.all()
    f = ResultFilter(request.GET, queryset=qs)
    ctx = {'filter': f, }
    return render(request, 'result/result_filter.html', ctx)


@user_passes_test(user_is_verified)
def result_detail_view(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    student_results = student.results.all()
    semesters = list(Semester.objects.all())
    semester_results = {}
    active_semesters = []

    for semester in semesters:
        results = student_results.filter(semester=semester)
        if results:
            active_semesters.append(semester)
            semester_results.update(
                {f'{semester}': results}
            )
    ctx = {
        'student': student,
        'semester_results': semester_results,
        'active_semesters': active_semesters
    }
    return render(request, 'result/result_detail.html', ctx)


def find_student(request, student_id):
    """ Find student by given id for result entry."""
    student = Student.objects.get(
        temporary_id=student_id
    )
    ctx = {
        'student_name': student.admission_student.name,
        'student_batch': student.batch.number,
        'image_url': student.admission_student.photo.url
    }
    return JsonResponse({'data': ctx})


@user_passes_test(user_is_teacher_or_administrative)
def result_entry(request):
    if not request.GET:
        qs = SubjectGroup.objects.none()
    else:
        qs = SubjectGroup.objects.all()

    subject_group_filter = SubjectGroupFilter(
        request.GET,
        queryset=qs
    )

    if request.method == 'POST':
        data_items = request.POST.items()
        # get student from pk
        student_temp_id = request.POST.get('student_id')
        student = Student.objects.get(temporary_id=student_temp_id)
        semester = Semester.objects.get(pk=int(request.POST.get('semester')))

        result_created = {}
        for key, value in data_items:
            # get subject from pk
            if '.' in key:
                try:
                    s_pk = int(key.split('.')[1])
                    subject = Subject.objects.get(pk=s_pk)
                    if not result_created.get(str(s_pk)):
                        # get subject marks
                        practical_marks = int(
                            request.POST.get(f'practical_marks.{s_pk}')
                        )
                        theory_marks = int(
                            request.POST.get(f'theory_marks.{s_pk}')
                        )
                        result = Result(
                            student=student,
                            semester=semester,
                            subject=subject,
                            practical_marks=practical_marks,
                            theory_marks=theory_marks
                        )
                        try:
                            result.save()
                            result_created[str(s_pk)] = True
                        except IntegrityError:
                            messages.error(
                                request,
                                f'{student.admission_student.name}\'s result '
                                f'for {subject} has been created already.'
                            )
                except ValueError:
                    pass
        return redirect('result:result_entry')
    ctx = {
        'subject_group_filter': subject_group_filter,
    }
    return render(request, 'result/result_entry.html', ctx)


@user_passes_test(user_is_teacher_or_administrative)
def create_subject_group(request):
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()

    if request.method == 'POST':
        dept_pk = int(request.POST.get('department'))
        subject_list = request.POST.getlist('subject')
        semester_pk = int(request.POST.get('semester'))

        dept = Department.objects.get(pk=dept_pk)
        semester = Semester.objects.get(pk=semester_pk)

        subject_group = SubjectGroup.objects.create(
            department=dept,
            semester=semester
        )

        subject_objects = []
        for s_pk in subject_list:
            subj = Subject.objects.get(pk=int(s_pk))
            subject_objects.append(subj)
            subject_group.subjects.add(subj)

        subject_group.save()
        return redirect('result:subject_groups')
    ctx = {
        'departments': departments,
        'semesters': semesters,
        'subjects': subjects,
    }
    return render(request, 'result/create_subject_groups.html', ctx)


@user_passes_test(user_is_verified)
def subject_group_list(request):
    subject_groups = SubjectGroup.objects.all()
    ctx = {
        'subject_groups': subject_groups,
    }
    return render(request, 'result/subject_group_list.html', ctx)


# Teacher-specific views for mark entry
@user_passes_test(user_is_teacher)
def teacher_dashboard(request):
    """ Teacher dashboard showing their assigned subjects and quick actions """
    teacher = request.user.teacher_profile
    assigned_subjects = Subject.objects.filter(instructor=teacher)
    recent_results = Result.objects.filter(
        subject__in=assigned_subjects
    ).order_by('-created')[:5]
    recent_attendance = Attendance.objects.filter(
        subject__in=assigned_subjects
    ).order_by('-date')[:5]
    
    ctx = {
        'teacher': teacher,
        'assigned_subjects': assigned_subjects,
        'recent_results': recent_results,
        'recent_attendance': recent_attendance,
    }
    return render(request, 'result/teacher_dashboard.html', ctx)


@user_passes_test(user_is_teacher)
def teacher_mark_entry(request):
    """ Teacher-specific mark entry view """
    teacher = request.user.teacher_profile
    assigned_subjects = Subject.objects.filter(instructor=teacher)
    
    if request.method == 'POST':
        form = TeacherMarkEntryForm(request.POST)
        if form.is_valid():
            semester = form.cleaned_data['semester']
            subject = form.cleaned_data['subject']
            
            # Check if teacher is assigned to this subject
            if subject not in assigned_subjects:
                messages.error(request, "You are not assigned to this subject.")
                return redirect('result:teacher_mark_entry')
            
            # Get students enrolled in this semester and subject's department
            students = Student.objects.filter(
                semester=semester,
                admission_student__choosen_department=subject.department_choice
            ).order_by('admission_student__name')
            
            # Prepare initial data for formset
            initial_data = []
            for student in students:
                # Check if result already exists
                existing_result = Result.objects.filter(
                    student=student,
                    semester=semester,
                    subject=subject
                ).first()
                
                if existing_result:
                    initial_data.append({
                        'student': student,
                        'semester': semester,
                        'subject': subject,
                        'practical_marks': existing_result.practical_marks,
                        'theory_marks': existing_result.theory_marks,
                    })
                else:
                    initial_data.append({
                        'student': student,
                        'semester': semester,
                        'subject': subject,
                    })
            
            formset = ResultFormSet(
                queryset=Result.objects.none(),
                initial=initial_data
            )
            ctx = {
                'form': form,
                'formset': formset,
                'assigned_subjects': assigned_subjects,
            }
            return render(request, 'result/teacher_mark_entry.html', ctx)
    else:
        form = TeacherMarkEntryForm()
        ctx = {
            'form': form,
            'assigned_subjects': assigned_subjects,
        }
    return render(request, 'result/teacher_mark_entry.html', ctx)


@user_passes_test(user_is_teacher)
def teacher_attendance_entry(request):
    """ Teacher-specific attendance entry view """
    teacher = request.user.teacher_profile
    assigned_subjects = Subject.objects.filter(instructor=teacher)
    
    if request.method == 'POST':
        form = TeacherAttendanceEntryForm(request.POST)
        if form.is_valid():
            semester = form.cleaned_data['semester']
            subject = form.cleaned_data['subject']
            date = form.cleaned_data['date']
            
            # Check if teacher is assigned to this subject
            if subject not in assigned_subjects:
                messages.error(request, "You are not assigned to this subject.")
                return redirect('result:teacher_attendance_entry')
            
            # Get students enrolled in this semester and subject's department
            students = Student.objects.filter(
                semester=semester,
                admission_student__choosen_department=subject.department_choice
            ).order_by('admission_student__name')
            
            # Prepare initial data for formset
            initial_data = []
            for student in students:
                # Check if attendance already exists for this date
                existing_attendance = Attendance.objects.filter(
                    student=student,
                    subject=subject,
                    semester=semester,
                    date=date
                ).first()
                
                if existing_attendance:
                    initial_data.append({
                        'student': student,
                        'subject': subject,
                        'semester': semester,
                        'date': date,
                        'status': existing_attendance.status,
                    })
                else:
                    initial_data.append({
                        'student': student,
                        'subject': subject,
                        'semester': semester,
                        'date': date,
                    })
            
            formset = AttendanceFormSet(
                queryset=Attendance.objects.none(),
                initial=initial_data
            )
            ctx = {
                'form': form,
                'formset': formset,
                'assigned_subjects': assigned_subjects,
            }
            return render(request, 'result/teacher_attendance_entry.html', ctx)
    else:
        form = TeacherAttendanceEntryForm()
        ctx = {
            'form': form,
            'assigned_subjects': assigned_subjects,
        }
    return render(request, 'result/teacher_attendance_entry.html', ctx)


@user_passes_test(user_is_teacher)
def teacher_view_results(request):
    """ Teacher can view results for their assigned subjects """
    teacher = request.user.teacher_profile
    assigned_subjects = Subject.objects.filter(instructor=teacher)
    results = Result.objects.filter(subject__in=assigned_subjects).order_by('-created')
    
    ctx = {
        'results': results,
        'assigned_subjects': assigned_subjects,
    }
    return render(request, 'result/teacher_view_results.html', ctx)


@user_passes_test(user_is_teacher)
def teacher_view_attendance(request):
    """ Teacher can view attendance for their assigned subjects """
    teacher = request.user.teacher_profile
    assigned_subjects = Subject.objects.filter(instructor=teacher)
    attendance_records = Attendance.objects.filter(subject__in=assigned_subjects).order_by('-date')
    
    ctx = {
        'attendance_records': attendance_records,
        'assigned_subjects': assigned_subjects,
    }
    return render(request, 'result/teacher_view_attendance.html', ctx)