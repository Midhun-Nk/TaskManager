from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Task
from .serializers import TaskSerializer, TaskUpdateSerializer
from .permissions import IsTaskOwner, IsAdminOrSuperAdmin

class UserTasksListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user).order_by('-due_date', '-created_at')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwner]

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        # check object permission (IsTaskOwner)
        self.check_object_permissions(request, task)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # return full task representation
        full = TaskSerializer(task)
        return Response(full.data)

class TaskReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.status != Task.STATUS_COMPLETED:
            return Response({"detail":"Task must be completed to view the report."}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            "id": task.id,
            "title": task.title,
            "assigned_to": task.assigned_to.username,
            "completion_report": task.completion_report,
            "worked_hours": str(task.worked_hours),
            "completed_at": task.updated_at,
        }
        return Response(data)
