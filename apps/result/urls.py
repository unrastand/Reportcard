from django.urls import path

from . import views


app_name = "result"

urlpatterns = [
    path('', views.result_view, name='result'),
    path('<int:student_pk>/details/', views.result_detail_view, name='result_details'),
    path('entry/', views.result_entry, name='result_entry'),
    path('create/subject-group/', views.create_subject_group, name='create_subject_group'),
    path('subject-groups/', views.subject_group_list, name='subject_groups'),
    path('find-student/<str:student_id>/', views.find_student, name='find_student'),
    
    # Teacher-specific URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/mark-entry/', views.teacher_mark_entry, name='teacher_mark_entry'),
    path('teacher/attendance-entry/', views.teacher_attendance_entry, name='teacher_attendance_entry'),
    path('teacher/view-results/', views.teacher_view_results, name='teacher_view_results'),
    path('teacher/view-attendance/', views.teacher_view_attendance, name='teacher_view_attendance'),
]