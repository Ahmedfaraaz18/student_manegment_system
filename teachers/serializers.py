from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.tenancy import get_user_institution
from core.services.sms_service import send_teacher_credentials
from tenants.services import enforce_usage_limit

from .models import Teacher

User = get_user_model()
DEFAULT_PASSWORD = "default123"


class TeacherSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = Teacher
        fields = ["id", "name", "email", "phone", "institution_name", "department", "department_name", "generated_password"]

    def validate_department(self, department):
        institution = get_user_institution(self.context["request"].user)
        if institution and department.institution_id != institution.id:
            raise serializers.ValidationError("Department must belong to your institution.")
        return department

    def create(self, validated_data):
        institution = get_user_institution(self.context["request"].user)
        enforce_usage_limit(institution, "teachers")
        user = User.all_objects.filter(username=validated_data["email"]).first()
        created = False
        if user is None:
            user = User(
                username=validated_data["email"],
                email=validated_data["email"],
                role=User.TEACHER,
                first_name=validated_data["name"],
                institution=institution,
            )
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            created = True

        teacher = Teacher.objects.create(institution=institution, user=user, **validated_data)
        teacher.generated_password = DEFAULT_PASSWORD if created else "existing-account"
        if created:
            send_teacher_credentials(teacher, user.username, DEFAULT_PASSWORD)
        return teacher

    def update(self, instance, validated_data):
        old_email = instance.email
        teacher = super().update(instance, validated_data)
        if teacher.user:
            teacher.user.email = teacher.email
            teacher.user.first_name = teacher.name
            teacher.user.institution = teacher.institution
            if teacher.user.username == old_email:
                teacher.user.username = teacher.email
            teacher.user.save()
        return teacher
