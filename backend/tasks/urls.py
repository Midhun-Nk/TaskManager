from django.urls import path
from .views import UserTasksListAPIView, TaskUpdateAPIView, TaskReportAPIView

urlpatterns = [
    path('tasks/', UserTasksListAPIView.as_view(), name='user-tasks'),
    path('tasks/<int:pk>/', TaskUpdateAPIView.as_view(), name='task-update'),
    path('tasks/<int:pk>/report/', TaskReportAPIView.as_view(), name='task-report'),
]
