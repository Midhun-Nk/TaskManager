from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.StringRelatedField(read_only=True)  # returns username

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'due_date', 'status', 'completion_report', 'worked_hours', 'created_at']
        read_only_fields = ['id', 'assigned_to', 'created_at']

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status', 'completion_report', 'worked_hours']

    def validate(self, attrs):
        # If status is being set to COMPLETED => completion_report and worked_hours required
        status = attrs.get('status', None)
        if status == Task.STATUS_COMPLETED:
            report = attrs.get('completion_report') or self.instance.completion_report
            hours = attrs.get('worked_hours') or self.instance.worked_hours
            if not report:
                raise serializers.ValidationError({"completion_report":"This field is required when marking as completed."})
            if hours is None:
                raise serializers.ValidationError({"worked_hours":"This field is required when marking as completed."})
            # optionally validate worked_hours > 0
            try:
                if float(hours) < 0:
                    raise serializers.ValidationError({"worked_hours":"Value must be non-negative."})
            except (TypeError, ValueError):
                raise serializers.ValidationError({"worked_hours":"Provide a numeric value."})
        return attrs
