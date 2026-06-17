from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from core.managers import apply_tenant_filter


class TenantAwareUserManager(UserManager):
    def get_queryset(self):
        return apply_tenant_filter(super().get_queryset(), self.model)


class Institution(models.Model):
    COLLEGE = "college"
    SCHOOL = "school"

    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    DELETED = "deleted"

    TYPE_CHOICES = (
        (COLLEGE, "College"),
        (SCHOOL, "School"),
    )

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (EXPIRED, "Expired"),
        (DELETED, "Deleted"),
    )

    name = models.CharField(max_length=200)
    code = models.SlugField(max_length=50, unique=True)
    institution_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=COLLEGE)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_institutions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InstitutionSettings(models.Model):
    institution = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name="settings")
    short_name = models.CharField(max_length=80, blank=True)
    primary_color = models.CharField(max_length=20, default="#11243d")
    support_email = models.EmailField(blank=True)
    attendance_threshold = models.PositiveSmallIntegerField(default=75)
    grading_scheme = models.TextField(
        default="A+: 90-100\nA: 80-89\nB: 70-79\nC: 60-69\nD: 50-59\nF: Below 50"
    )
    current_academic_year = models.CharField(max_length=20, blank=True)
    logo_url = models.URLField(blank=True)

    def __str__(self):
        return f"Settings for {self.institution.name}"


class User(AbstractUser):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    HOD = "hod"
    EXAM_OFFICER = "exam_officer"
    PLACEMENT_OFFICER = "placement_officer"
    ACCOUNTANT = "accountant"
    TEACHER = "teacher"
    STUDENT = "student"

    ROLE_CHOICES = (
        (SUPER_ADMIN, "Super Admin"),
        (ADMIN, "Admin"),
        (HOD, "Head Of Department"),
        (EXAM_OFFICER, "Exam Officer"),
        (PLACEMENT_OFFICER, "Placement Officer"),
        (ACCOUNTANT, "Accountant"),
        (TEACHER, "Teacher"),
        (STUDENT, "Student"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    objects = TenantAwareUserManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    def save(self, *args, **kwargs):
        if self.is_superuser and self.institution_id is None:
            self.role = self.SUPER_ADMIN
            self.is_staff = True
        elif self.is_superuser:
            self.role = self.ADMIN
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
