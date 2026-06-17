from rest_framework.throttling import UserRateThrottle


class AIChatRateThrottle(UserRateThrottle):
    scope = "ai_chat"

