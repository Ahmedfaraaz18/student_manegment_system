from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Announcement
        fields = ["id", "title", "message", "created_by", "created_by_name", "created_at", "institution_name"]
        read_only_fields = ["created_by", "created_at"]
