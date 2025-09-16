from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('login/', views.panel_login, name='login'),
    path('logout/', views.panel_logout, name='logout'),

    path('super/dashboard/', views.super_dashboard, name='super-dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),

    path('users/', views.users_list, name='users-list'),
    path('users/create/', views.user_create, name='user-create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user-edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user-delete'),

    path('tasks/', views.tasks_list, name='tasks-list'),
    path('tasks/create/', views.task_create, name='task-create'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task-edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task-delete'),
    path('tasks/<int:pk>/report/', views.task_report_view, name='task-report'),
    path('user/tasks/', views.user_tasks, name='user-tasks'),
    path('user/tasks/<int:pk>/complete/', views.user_complete_task, name='user-complete-task'),
    path('tasks/export/', views.export_task_reports, name='export-tasks'),



]
