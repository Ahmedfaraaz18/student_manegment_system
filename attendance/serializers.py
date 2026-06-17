from rest_framework import serializers

from accounts.tenancy import get_user_institution

from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "student", "student_name", "subject", "subject_name", "institution_name", "date", "status"]

    def validate(self, attrs):
        student = attrs.get("student") or getattr(self.instance, "student", None)
        subject = attrs.get("subject") or getattr(self.instance, "subject", None)
        institution = get_user_institution(self.context["request"].user)
        if institution is None:
            raise serializers.ValidationError("Institution context is required.")
        if student and student.institution_id != institution.id:
            raise serializers.ValidationError({"student": "Student must belong to your institution."})
        if subject and subject.institution_id != institution.id:
            raise serializers.ValidationError({"subject": "Subject must belong to your institution."})
        if student and subject and student.department_id != subject.department_id:
            raise serializers.ValidationError("Attendance can only be marked for students in the subject department.")
        return attrs


class AttendanceBulkSerializer(serializers.Serializer):
    subject = serializers.IntegerField()
    date = serializers.DateField()
    records = serializers.ListField(child=serializers.DictField(), allow_empty=False)
