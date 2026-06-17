from rest_framework import serializers

from .models import ApprovalRequest


class ApprovalRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source="requested_by.username", read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            "id",
            "request_type",
            "title",
            "description",
            "status",
            "decision_notes",
            "requested_by",
            "requested_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["requested_by", "created_at", "updated_at"]
