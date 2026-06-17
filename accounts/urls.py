from django.urls import path

from .views import InstitutionSettingsView, me

urlpatterns = [
    path("settings/", InstitutionSettingsView.as_view()),
    path("me/", me),
]
