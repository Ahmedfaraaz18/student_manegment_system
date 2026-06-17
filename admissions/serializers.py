from rest_framework import serializers

from accounts.tenancy import get_user_institution

from .models import AdmissionApplication


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    program_name = serializers.CharField(source="program.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = [
            "id",
            "applicant_name",
            "email",
            "phone",
            "previous_qualification",
            "academic_year",
            "academic_year_name",
            "program",
            "program_name",
            "section",
            "section_name",
            "status",
            "notes",
            "created_at",
        ]

    def validate(self, attrs):
        institution = get_user_institution(self.context["request"].user)
        academic_year = attrs.get("academic_year") or getattr(self.instance, "academic_year", None)
        program = attrs.get("program") or getattr(self.instance, "program", None)
        section = attrs.get("section") or getattr(self.instance, "section", None)
        if institution is None:
            raise serializers.ValidationError("Institution context is required.")
        if academic_year and academic_year.institution_id != institution.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to your institution."})
        if program and program.institution_id != institution.id:
            raise serializers.ValidationError({"program": "Program must belong to your institution."})
        if section and section.institution_id != institution.id:
            raise serializers.ValidationError({"section": "Section must belong to your institution."})
        return attrs
