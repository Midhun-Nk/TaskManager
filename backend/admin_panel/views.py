from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from accounts.models import User
from tasks.models import Task
from .forms import UserCreateForm, UserUpdateForm, TaskForm
from .permissions import is_superadmin, is_admin, is_superadmin_or_admin

# Simple login/logout views for panel (optional; useful if using session auth)
def panel_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # redirect based on role
            if user.role == User.Role.SUPERADMIN:
                return redirect('admin_panel:super-dashboard')
            if user.role == User.Role.ADMIN:
                return redirect('admin_panel:admin-dashboard')
            return redirect('admin_panel:user-tasks')  # user view
        messages.error(request, 'Invalid credentials')
    return render(request, 'admin_panel/login.html')

def panel_logout(request):
    logout(request)
    return redirect('admin_panel:login')

# SuperAdmin dashboard
@login_required
@is_superadmin
def super_dashboard(request):
    total_users = User.objects.filter(role=User.Role.USER).count()
    total_admins = User.objects.filter(role=User.Role.ADMIN).count()
    total_tasks = Task.objects.count()
    context = {'total_users': total_users, 'total_admins': total_admins, 'total_tasks': total_tasks}
    return render(request, 'admin_panel/super_dashboard.html', context)

# Admin dashboard
@login_required
@is_admin
def admin_dashboard(request):
    # Admin sees tasks assigned to users they manage OR tasks created by them (if you track creator)
    managed_users = request.user.managed_users.all()  # via assigned_admin FK
    tasks = Task.objects.filter(assigned_to__in=managed_users)
    context = {'tasks': tasks, 'managed_users': managed_users}
    return render(request, 'admin_panel/admin_dashboard.html', context)

# List users (superadmin)
@login_required
@is_superadmin
def users_list(request):
    users = User.objects.exclude(role=User.Role.SUPERADMIN)
    return render(request, 'admin_panel/users_list.html', {'users': users})

@login_required
@is_superadmin
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User created')
            return redirect('admin_panel:users-list')
    else:
        form = UserCreateForm()
    return render(request, 'admin_panel/user_form.html', {'form': form, 'create': True})

@login_required
@is_superadmin
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated')
            return redirect('admin_panel:users-list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'admin_panel/user_form.html', {'form': form, 'create': False, 'user_obj': user})

@login_required
@is_superadmin
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted')
        return redirect('admin_panel:users-list')
    return render(request, 'admin_panel/user_confirm_delete.html', {'user_obj': user})

# Tasks management (superadmin and admin)
@login_required
@is_superadmin_or_admin
def tasks_list(request):
    user = request.user
    if user.role == User.Role.SUPERADMIN:
        tasks = Task.objects.select_related('assigned_to').all()
    else:  # admin
        managed_users = user.managed_users.all()
        tasks = Task.objects.filter(assigned_to__in=managed_users)
    return render(request, 'admin_panel/tasks_list.html', {'tasks': tasks})

@login_required
@is_superadmin_or_admin
def task_create(request):
    user = request.user
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task created')
            return redirect('admin_panel:tasks-list')
    else:
        form = TaskForm()
        # For admin, restrict assigned_to choices to their managed users
        if user.role == User.Role.ADMIN:
            form.fields['assigned_to'].queryset = user.managed_users.all()
    return render(request, 'admin_panel/task_form.html', {'form': form, 'create': True})

@login_required
@is_superadmin_or_admin
def task_edit(request, pk):
    user = request.user
    task = get_object_or_404(Task, pk=pk)
    # Admin should only edit tasks assigned to their users
    if user.role == User.Role.ADMIN and task.assigned_to.assigned_admin != user:
        return HttpResponseForbidden("Not allowed")
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if user.role == User.Role.ADMIN:
            form.fields['assigned_to'].queryset = user.managed_users.all()
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated')
            return redirect('admin_panel:tasks-list')
    else:
        form = TaskForm(instance=task)
        if user.role == User.Role.ADMIN:
            form.fields['assigned_to'].queryset = user.managed_users.all()
    return render(request, 'admin_panel/task_form.html', {'form': form, 'create': False, 'task': task})

@login_required
@is_superadmin_or_admin
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    if user.role == User.Role.ADMIN and task.assigned_to.assigned_admin != user:
        return HttpResponseForbidden("Not allowed")
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted')
        return redirect('admin_panel:tasks-list')
    return render(request, 'admin_panel/task_confirm_delete.html', {'task': task})

# View completion report (admin & superadmin)
@login_required
@is_superadmin_or_admin
def task_report_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Admins only see reports for tasks assigned to their users
    if request.user.role == User.Role.ADMIN and task.assigned_to.assigned_admin != request.user:
        return HttpResponseForbidden("Not allowed")
    if task.status != Task.STATUS_COMPLETED:
        messages.warning(request, 'Task not completed yet.')
    return render(request, 'admin_panel/task_report.html', {'task': task})

@login_required
def user_tasks(request):
    tasks = request.user.tasks.all()  # because Task.assigned_to = user
    return render(request, 'admin_panel/user_tasks.html', {'tasks': tasks})



@login_required
def user_complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)

    if task.status == Task.STATUS_COMPLETED:
        messages.info(request, "Task already completed.")
        return redirect('admin_panel:user-tasks')

    if request.method == "POST":
        # Only allow updating status, completion_report, worked_hours
        task.status = Task.STATUS_COMPLETED
        task.completion_report = request.POST.get("completion_report")
        task.worked_hours = request.POST.get("worked_hours")

        if not task.completion_report or not task.worked_hours:
            messages.error(request, "Completion report and worked hours are required.")
            return redirect('admin_panel:user-complete-task', pk=pk)

        task.save()
        messages.success(request, "Task marked as completed!")
        return redirect('admin_panel:user-tasks')

    return render(request, "admin_panel/user_complete_task.html", {"task": task})

import csv
from django.http import HttpResponse

@login_required
@is_superadmin
def export_task_reports(request):
    tasks = Task.objects.filter(status=Task.STATUS_COMPLETED)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="task_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Assigned To', 'Completion Report', 'Worked Hours', 'Completed At'])

    for t in tasks:
        writer.writerow([t.id, t.title, t.assigned_to.username, t.completion_report, t.worked_hours, t.updated_at])

    return response
