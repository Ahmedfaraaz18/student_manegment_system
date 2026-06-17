import logging
import os

import requests


logger = logging.getLogger(__name__)

MESSAGE_PROVIDER = os.getenv("MESSAGE_PROVIDER", "console").strip().lower()
DEFAULT_SENDER_ID = os.getenv("ERP_SMS_SENDER_ID", "ERPAPP")
ERP_APP_NAME = os.getenv("ERP_APP_NAME", "EduERP").strip() or "EduERP"


def _provider_not_configured(detail):
    return {"status": "failed", "provider": MESSAGE_PROVIDER, "detail": detail}


def _console_message(phone, message):
    logger.info("ERP message to %s via console: %s", phone, message)
    return {"status": "logged", "provider": "console", "phone": phone}


def _fast2sms_message(phone, message):
    api_key = os.getenv("FAST2SMS_API_KEY", "").strip()
    if not api_key:
        return _provider_not_configured("FAST2SMS_API_KEY is not configured.")

    payload = {
        "sender_id": DEFAULT_SENDER_ID,
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": phone,
    }
    headers = {"authorization": api_key}

    try:
        response = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            data=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return {"status": "sent", "provider": "fast2sms", "response": response.json()}
    except requests.RequestException as exc:
        return {"status": "failed", "provider": "fast2sms", "detail": str(exc)}


def _twilio_message(phone, message):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    if not account_sid or not auth_token or not from_number:
        return _provider_not_configured(
            "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER are required."
        )

    try:
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
            data={"To": phone, "From": from_number, "Body": message},
            auth=(account_sid, auth_token),
            timeout=10,
        )
        response.raise_for_status()
        return {"status": "sent", "provider": "twilio", "response": response.json()}
    except requests.RequestException as exc:
        return {"status": "failed", "provider": "twilio", "detail": str(exc)}


def send_sms(phone, message):
    if not phone:
        return {"status": "skipped", "detail": "Phone number is missing."}

    provider = MESSAGE_PROVIDER
    if provider == "console":
        return _console_message(phone, message)
    if provider == "fast2sms":
        return _fast2sms_message(phone, message)
    if provider == "twilio":
        return _twilio_message(phone, message)
    return {"status": "failed", "provider": provider, "detail": "Unsupported messaging provider."}


def send_message(phone, message):
    return send_sms(phone, message)


def send_student_credentials(student, username, password):
    message = (
        f"{ERP_APP_NAME} Login\n\n"
        f"Username: {username}\n"
        f"Password: {password}\n\n"
        f"Login to the ERP portal."
    )
    phone = getattr(student, "phone", None) or getattr(student, "parent_phone", "")
    return send_sms(phone, message)


def send_teacher_credentials(teacher, username, password):
    message = (
        f"{ERP_APP_NAME} Teacher Login\n\n"
        f"Username: {username}\n"
        f"Password: {password}"
    )
    return send_sms(getattr(teacher, "phone", ""), message)


def send_absent_sms(student):
    message = (
        f"Attendance Alert\n\n"
        f"{getattr(student, 'name', 'Student')} was absent today.\n\n"
        f"{ERP_APP_NAME}"
    )
    phone = getattr(student, "phone", None) or getattr(student, "parent_phone", "")
    return send_sms(phone, message)
