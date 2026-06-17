from rest_framework import serializers

from accounts.tenancy import get_user_institution

from .models import Placement


class PlacementSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Placement
        fields = ["id", "student", "student_name", "company", "package", "year", "institution_name"]

    def validate_student(self, student):
        institution = get_user_institution(self.context["request"].user)
        if institution and student.institution_id != institution.id:
            raise serializers.ValidationError("Student must belong to your institution.")
        return student
