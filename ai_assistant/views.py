from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AIChatRequestSerializer, AIChatSerializer
from .services import build_automation_briefing, generate_ai_reply
from .throttles import AIChatRateThrottle


class AIChatView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIChatRateThrottle]

    def get(self, request, *args, **kwargs):
        history = request.user.ai_chats.select_related("institution").all()[:20]
        serializer = AIChatSerializer(history, many=True)
        return Response({"history": list(reversed(serializer.data))})

    def post(self, request, *args, **kwargs):
        serializer = AIChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = generate_ai_reply(request.user, serializer.validated_data["message"])
        return Response(AIChatSerializer(chat).data, status=201)


class AIBriefingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(build_automation_briefing(request.user))
