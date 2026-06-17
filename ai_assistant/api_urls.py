from django.urls import path

from .views import AIBriefingView, AIChatView

urlpatterns = [
    path("chat/", AIChatView.as_view()),
    path("briefing/", AIBriefingView.as_view()),
]
