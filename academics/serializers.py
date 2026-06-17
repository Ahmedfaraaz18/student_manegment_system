from rest_framework import serializers

from accounts.tenancy import get_user_institution

from .models import AcademicYear, Program, Section


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "name", "start_date", "end_date", "is_current"]


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Program
        fields = ["id", "name", "code", "duration_years", "department", "department_name"]

    def validate_department(self, department):
        institution = get_user_institution(self.context["request"].user)
        if institution and department.institution_id != institution.id:
            raise serializers.ValidationError("Department must belong to your institution.")
        return department


class SectionSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    program_name = serializers.CharField(source="program.name", read_only=True)

    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "semester",
            "capacity",
            "academic_year",
            "academic_year_name",
            "program",
            "program_name",
        ]

    def validate(self, attrs):
        institution = get_user_institution(self.context["request"].user)
        academic_year = attrs.get("academic_year") or getattr(self.instance, "academic_year", None)
        program = attrs.get("program") or getattr(self.instance, "program", None)
        if institution is None:
            raise serializers.ValidationError("Institution context is required.")
        if academic_year and academic_year.institution_id != institution.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to your institution."})
        if program and program.institution_id != institution.id:
            raise serializers.ValidationError({"program": "Program must belong to your institution."})
        return attrs
