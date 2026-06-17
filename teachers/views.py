from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from .models import Teacher
from core.services.sms_service import send_teacher_credentials

User = get_user_model()


class TeacherListView(ListView):
    model = Teacher
    template_name = "teachers/list.html"
    context_object_name = "teachers"


class TeacherCreateView(CreateView):
    model = Teacher
    fields = ["name", "email", "institution", "department", "phone"]
    template_name = "teachers/form.html"
    success_url = reverse_lazy("teacher_list")

    def form_valid(self, form):
        email = (form.instance.email or "").strip().lower()
        base_username = email.split("@")[0] if "@" in email else email or "teacher"
        username = base_username
        counter = 1
        while User.all_objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        password = "teacher123"
        user = User(
            username=username,
            role=User.TEACHER,
            institution=form.instance.institution,
            email=form.instance.email,
            first_name=form.instance.name,
        )
        user.set_password(password)
        user.save()
        form.instance.user = user
        response = super().form_valid(form)
        teacher = self.object
        send_teacher_credentials(teacher, username, password)

        return response


class TeacherUpdateView(UpdateView):
    model = Teacher
    fields = ["name", "email", "institution", "department", "phone"]
    template_name = "teachers/form.html"
    success_url = reverse_lazy("teacher_list")


class TeacherDeleteView(DeleteView):
    model = Teacher
    template_name = "teachers/confirm_delete.html"
    success_url = reverse_lazy("teacher_list")
