from rest_framework import serializers

from accounts.tenancy import get_user_institution

from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "name", "institution_name", "department", "department_name", "teacher", "teacher_name"]

    def validate(self, attrs):
        department = attrs.get("department") or getattr(self.instance, "department", None)
        teacher = attrs.get("teacher") or getattr(self.instance, "teacher", None)
        institution = get_user_institution(self.context["request"].user)
        if institution is None:
            raise serializers.ValidationError("Institution context is required.")
        if department and department.institution_id != institution.id:
            raise serializers.ValidationError({"department": "Department must belong to your institution."})
        if teacher and teacher.institution_id != institution.id:
            raise serializers.ValidationError({"teacher": "Teacher must belong to your institution."})
        if department and teacher and department.institution_id != teacher.institution_id:
            raise serializers.ValidationError("Teacher and department must belong to the same institution.")
        return attrs
