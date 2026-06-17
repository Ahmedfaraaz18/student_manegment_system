from rest_framework import serializers

from .models import AIChat


class AIChatSerializer(serializers.ModelSerializer):
    user_message = serializers.CharField(source="message", read_only=True)
    assistant_message = serializers.CharField(source="response", read_only=True)

    class Meta:
        model = AIChat
        fields = (
            "id",
            "role_context",
            "user_message",
            "assistant_message",
            "provider",
            "model_name",
            "metadata",
            "created_at",
        )


class AIChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000, trim_whitespace=True)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()

