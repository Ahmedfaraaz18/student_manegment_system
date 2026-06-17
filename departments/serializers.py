from rest_framework import serializers

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "institution_name"]
