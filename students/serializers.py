from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.tenancy import get_user_institution
from tenants.services import enforce_usage_limit

from .models import Student

User = get_user_model()
DEFAULT_PASSWORD = "default123"


class StudentSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ["id", "name", "email", "year", "institution_name", "department", "department_name", "generated_password"]

    def validate_department(self, department):
        institution = get_user_institution(self.context["request"].user)
        if institution and department.institution_id != institution.id:
            raise serializers.ValidationError("Department must belong to your institution.")
        return department

    def create(self, validated_data):
        institution = get_user_institution(self.context["request"].user)
        enforce_usage_limit(institution, "students")
        user = User.all_objects.filter(username=validated_data["email"]).first()
        created = False
        if user is None:
            user = User(
                username=validated_data["email"],
                email=validated_data["email"],
                role=User.STUDENT,
                first_name=validated_data["name"],
                institution=institution,
            )
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            created = True

        student = Student.objects.create(institution=institution, user=user, **validated_data)
        student.generated_password = DEFAULT_PASSWORD if created else "existing-account"
        return student

    def update(self, instance, validated_data):
        old_email = instance.email
        student = super().update(instance, validated_data)
        if student.user:
            student.user.email = student.email
            student.user.first_name = student.name
            student.user.institution = student.institution
            if student.user.username == old_email:
                student.user.username = student.email
            student.user.save()
        return student
