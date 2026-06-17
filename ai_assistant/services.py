import os
from decimal import Decimal

import requests
from django.db.models import Avg, Count, F, Q, Sum
from rest_framework.exceptions import PermissionDenied

from accounts.models import Institution
from accounts.permissions import ADMIN_ROLES
from accounts.tenancy import get_user_institution
from admissions.models import AdmissionApplication
from announcements.models import Announcement
from attendance.models import Attendance
from fees.models import FeeInvoice, FeePayment
from results.models import Result
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher
from timetable.models import Timetable
from workflows.models import ApprovalRequest

from .models import AIChat


def resolve_role_context(user):
    if user.role == "student":
        return AIChat.ROLE_STUDENT
    if user.role == "teacher":
        return AIChat.ROLE_TEACHER
    if user.role == "super_admin" or user.role in ADMIN_ROLES:
        return AIChat.ROLE_ADMIN
    raise PermissionDenied("Your role is not allowed to access the AI assistant.")


def _to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def _student_context(user, institution):
    student = getattr(user, "student_profile", None)
    if student is None:
        raise PermissionDenied("Student profile not found for this account.")

    attendance_qs = Attendance.objects.filter(student=student).select_related("subject")
    attendance_totals = attendance_qs.aggregate(
        total=Count("id"),
        present=Count("id", filter=Q(status=Attendance.PRESENT)),
    )
    attendance_total = attendance_totals["total"] or 0
    attendance_present = attendance_totals["present"] or 0
    attendance_percentage = round((attendance_present / attendance_total) * 100, 2) if attendance_total else 0
    subject_attendance = []
    for row in (
        attendance_qs.values("subject__name")
        .annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status=Attendance.PRESENT)),
        )
        .order_by("subject__name")
    ):
        total = row["total"] or 0
        present = row["present"] or 0
        subject_attendance.append(
            {
                "subject": row["subject__name"],
                "percentage": round((present / total) * 100, 2) if total else 0,
                "present": present,
                "total": total,
            }
        )

    results = list(
        Result.objects.filter(student=student)
        .select_related("subject", "exam")
        .values("subject__name", "exam__name", "marks")
        .order_by("-marks", "subject__name")[:10]
    )
    timetable_entries = list(
        Timetable.objects.filter(department=student.department)
        .select_related("subject", "teacher")
        .values("day", "time_slot", "subject__name", "teacher__name")
        .order_by("day", "time_slot")[:12]
    )
    announcements = list(
        Announcement.objects.filter(institution=institution).values("title", "created_at").order_by("-created_at")[:5]
    )

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "department": student.department.name,
            "year": student.year,
        },
        "attendance": {
            "percentage": attendance_percentage,
            "present": attendance_present,
            "total": attendance_total,
            "by_subject": subject_attendance,
        },
        "results": results,
        "timetable": timetable_entries,
        "assignments_supported": False,
        "recent_announcements": announcements,
    }


def _teacher_context(user, institution):
    teacher = getattr(user, "teacher_profile", None)
    if teacher is None:
        raise PermissionDenied("Teacher profile not found for this account.")

    subject_ids = list(Subject.objects.filter(teacher=teacher).values_list("id", flat=True))
    attendance_rows = (
        Attendance.objects.filter(subject_id__in=subject_ids)
        .values(student_name=F("student__name"))
        .annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status=Attendance.PRESENT)),
        )
        .order_by("student_name")
    )
    low_attendance_students = []
    for row in attendance_rows:
        total = row["total"] or 0
        present = row["present"] or 0
        percentage = round((present / total) * 100, 2) if total else 0
        if total and percentage < 75:
            low_attendance_students.append(
                {
                    "student": row["student_name"],
                    "percentage": percentage,
                    "present": present,
                    "total": total,
                }
            )
    low_attendance_students = sorted(low_attendance_students, key=lambda item: item["percentage"])[:10]

    performance_rows = (
        Result.objects.filter(subject__teacher=teacher)
        .values("student__name")
        .annotate(avg_marks=Avg("marks"), records=Count("id"))
        .order_by("avg_marks")
    )
    weakest_performers = [
        {
            "student": row["student__name"],
            "average_marks": round(row["avg_marks"] or 0, 2),
            "records": row["records"],
        }
        for row in performance_rows[:10]
    ]
    strongest_performers = [
        {
            "student": row["student__name"],
            "average_marks": round(row["avg_marks"] or 0, 2),
            "records": row["records"],
        }
        for row in performance_rows.order_by("-avg_marks")[:10]
    ]

    subject_summaries = list(
        Subject.objects.filter(teacher=teacher)
        .values("name", "department__name")
        .annotate(student_count=Count("attendance_records__student", distinct=True))
        .order_by("name")
    )

    return {
        "teacher": {
            "id": teacher.id,
            "name": teacher.name,
            "department": teacher.department.name,
        },
        "subjects": subject_summaries,
        "low_attendance_students": low_attendance_students,
        "performance_insights": {
            "weakest_performers": weakest_performers,
            "strongest_performers": strongest_performers,
        },
    }


def _admin_context(user, institution):
    if institution is None:
        return {
            "platform": {
                "institutions": Institution.objects.count(),
                "students": Student.all_objects.count(),
                "teachers": Teacher.all_objects.count(),
            },
            "complaints_supported": False,
        }

    fee_totals = FeeInvoice.objects.filter(institution=institution).aggregate(
        total_invoiced=Sum("amount"),
        total_paid=Sum("amount_paid"),
    )
    total_invoiced = fee_totals["total_invoiced"] or Decimal("0")
    total_paid = fee_totals["total_paid"] or Decimal("0")
    pending_amount = total_invoiced - total_paid

    admissions_summary = list(
        AdmissionApplication.objects.filter(institution=institution)
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    approvals_summary = list(
        ApprovalRequest.objects.filter(institution=institution)
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    announcement_titles = list(
        Announcement.objects.filter(institution=institution).values("title", "created_at").order_by("-created_at")[:5]
    )
    payment_summary = list(
        FeePayment.objects.filter(institution=institution)
        .values("mode")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )

    return {
        "institution": {
            "id": institution.id,
            "name": institution.name,
            "type": institution.institution_type,
        },
        "revenue": {
            "total_invoiced": _to_float(total_invoiced),
            "total_paid": _to_float(total_paid),
            "pending_amount": _to_float(pending_amount),
            "open_invoices": FeeInvoice.objects.filter(institution=institution).exclude(status=FeeInvoice.PAID).count(),
            "payment_modes": [{**item, "total": _to_float(item["total"] or 0)} for item in payment_summary],
        },
        "admissions": admissions_summary,
        "approvals": approvals_summary,
        "recent_announcements": announcement_titles,
        "complaints_supported": False,
    }


def build_role_context(user):
    institution = get_user_institution(user)
    role_context = resolve_role_context(user)
    if role_context == AIChat.ROLE_STUDENT:
        context = _student_context(user, institution)
    elif role_context == AIChat.ROLE_TEACHER:
        context = _teacher_context(user, institution)
    else:
        context = _admin_context(user, institution)
    return role_context, institution, context


def _fallback_student_reply(message, context):
    lowered = message.lower()
    attendance = context["attendance"]
    if "attendance" in lowered:
        lines = [
            f"Your current attendance is {attendance['percentage']}% ({attendance['present']} of {attendance['total']} classes).",
        ]
        if attendance["by_subject"]:
            weakest = min(attendance["by_subject"], key=lambda item: item["percentage"])
            lines.append(
                f"Lowest attendance subject: {weakest['subject']} at {weakest['percentage']}%."
            )
        return " ".join(lines)
    if "mark" in lowered or "result" in lowered or "score" in lowered:
        if not context["results"]:
            return "No result records were found for your account yet."
        top = context["results"][0]
        return (
            f"Your highest recent score is {top['marks']} in {top['subject__name']}. "
            f"I found {len(context['results'])} recent result records."
        )
    if "timetable" in lowered or "schedule" in lowered or "class" in lowered:
        if not context["timetable"]:
            return "No timetable entries are configured for your department yet."
        next_item = context["timetable"][0]
        return (
            f"I found {len(context['timetable'])} timetable entries for your department. "
            f"The first listed slot is {next_item['day']} at {next_item['time_slot']} for {next_item['subject__name']}."
        )
    if "assignment" in lowered:
        return "Assignment data is not available in the current database schema yet, so I cannot fetch live assignment records."
    return (
        f"You are in {context['student']['department']} year {context['student']['year']}. "
        f"Attendance is {attendance['percentage']}%, and I found {len(context['results'])} recent result records."
    )


def _fallback_teacher_reply(message, context):
    lowered = message.lower()
    if "low attendance" in lowered or "attendance" in lowered:
        students = context["low_attendance_students"]
        if not students:
            return "No students below the 75% attendance threshold were found in your subject attendance records."
        preview = ", ".join(f"{item['student']} ({item['percentage']}%)" for item in students[:3])
        return f"Students with low attendance include {preview}. I found {len(students)} students below 75%."
    if "question" in lowered or "test" in lowered or "quiz" in lowered:
        subjects = ", ".join(item["name"] for item in context["subjects"][:3]) or "your assigned subjects"
        return (
            f"Draft test prompt: create a mixed-difficulty assessment for {subjects}, with 5 short-answer and 5 objective questions."
        )
    if "performance" in lowered or "analytic" in lowered or "insight" in lowered:
        weakest = context["performance_insights"]["weakest_performers"]
        if not weakest:
            return "No result records were found yet for your subjects, so performance insights are not available."
        item = weakest[0]
        return (
            f"Current lowest average performer is {item['student']} with an average of {item['average_marks']}. "
            f"I also computed top and bottom student groups from your result records."
        )
    return (
        f"You currently handle {len(context['subjects'])} subjects. "
        f"I found {len(context['low_attendance_students'])} students below the attendance threshold."
    )


def _fallback_admin_reply(message, context):
    lowered = message.lower()
    if "platform" in context:
        platform = context["platform"]
        return (
            f"Platform summary: {platform['institutions']} institutions, {platform['students']} students, "
            f"and {platform['teachers']} teachers are currently in the database."
        )
    if "fee" in lowered or "revenue" in lowered or "payment" in lowered:
        revenue = context["revenue"]
        return (
            f"Fee summary: invoiced {revenue['total_invoiced']}, collected {revenue['total_paid']}, pending {revenue['pending_amount']}. "
            f"There are {revenue['open_invoices']} unpaid or partially paid invoices."
        )
    if "admission" in lowered:
        items = ", ".join(f"{row['status']}: {row['count']}" for row in context["admissions"]) or "no admissions found"
        return f"Admission pipeline summary: {items}."
    if "complaint" in lowered:
        return "A complaint or grievance module is not present in the current project, so live complaint summaries are not available yet."
    if "announcement" in lowered:
        institution_name = context["institution"]["name"]
        return (
            f"Draft announcement for {institution_name}: Admissions and fee follow-ups are being reviewed this week. "
            f"Please check the portal for updated schedules and pending actions."
        )
    return (
        f"Institution summary for {context['institution']['name']}: "
        f"{len(context['admissions'])} admission status groups, {len(context['approvals'])} approval status groups, "
        f"and {context['revenue']['open_invoices']} open fee invoices."
    )


def build_fallback_reply(role_context, message, context):
    if role_context == AIChat.ROLE_STUDENT:
        return _fallback_student_reply(message, context)
    if role_context == AIChat.ROLE_TEACHER:
        return _fallback_teacher_reply(message, context)
    return _fallback_admin_reply(message, context)


def _format_currency(value):
    return f"{_to_float(value):,.2f}"


def _build_student_briefing(context):
    attendance = context["attendance"]
    results = context["results"]
    timetable = context["timetable"]
    announcements = context["recent_announcements"]
    top_result = results[0] if results else None
    weakest_attendance = (
        min(attendance["by_subject"], key=lambda item: item["percentage"])
        if attendance["by_subject"]
        else None
    )

    headline = f"{context['student']['name']} automation brief"
    summary = (
        f"Attendance is {attendance['percentage']}% across {attendance['total']} classes, "
        f"with {len(results)} recent result records and {len(announcements)} announcements."
    )
    sections = [
        {
            "title": "Attendance",
            "action": {"label": "Open dashboard", "path": "/student/dashboard"},
            "items": [
                {"label": "Overall", "value": f"{attendance['percentage']}%"},
                {"label": "Present classes", "value": f"{attendance['present']} / {attendance['total']}"},
                {
                    "label": "Needs attention",
                    "value": (
                        f"{weakest_attendance['subject']} ({weakest_attendance['percentage']}%)"
                        if weakest_attendance
                        else "No subject split available"
                    ),
                },
            ],
        },
        {
            "title": "Results",
            "action": {"label": "Open dashboard", "path": "/student/dashboard"},
            "items": [
                {"label": "Recent records", "value": str(len(results))},
                {
                    "label": "Top score",
                    "value": (
                        f"{top_result['subject__name']} - {top_result['marks']}"
                        if top_result
                        else "No results yet"
                    ),
                },
            ],
        },
        {
            "title": "Timetable",
            "action": {"label": "Open dashboard", "path": "/student/dashboard"},
            "items": [
                {"label": "Scheduled slots", "value": str(len(timetable))},
                {
                    "label": "First slot",
                    "value": (
                        f"{timetable[0]['day']} {timetable[0]['time_slot']} - {timetable[0]['subject__name']}"
                        if timetable
                        else "No timetable configured"
                    ),
                },
            ],
        },
        {
            "title": "Announcements",
            "action": {"label": "Open dashboard", "path": "/student/dashboard"},
            "items": [
                {"label": "Recent posts", "value": str(len(announcements))},
                {
                    "label": "Latest",
                    "value": announcements[0]["title"] if announcements else "No announcements yet",
                },
            ],
        },
    ]
    return {
        "headline": headline,
        "summary": summary,
        "sections": sections,
        "suggested_prompts": [
            "Show my attendance",
            "Summarize my recent results",
            "Show my timetable help",
        ],
    }


def _build_teacher_briefing(context):
    low_attendance = context["low_attendance_students"]
    weakest = context["performance_insights"]["weakest_performers"]
    strongest = context["performance_insights"]["strongest_performers"]
    subjects = context["subjects"]

    headline = f"{context['teacher']['name']} automation brief"
    summary = (
        f"You handle {len(subjects)} subjects, with {len(low_attendance)} students below attendance threshold "
        f"and {len(weakest)} students in the current low-performance snapshot."
    )
    sections = [
        {
            "title": "Teaching load",
            "action": {"label": "Open dashboard", "path": "/teacher/dashboard"},
            "items": [
                {"label": "Assigned subjects", "value": str(len(subjects))},
                {
                    "label": "Departments",
                    "value": ", ".join(sorted({item['department__name'] for item in subjects})) or "Not assigned",
                },
            ],
        },
        {
            "title": "Attendance alerts",
            "action": {"label": "Mark attendance", "path": "/admin/attendance"},
            "items": [
                {"label": "Below 75%", "value": str(len(low_attendance))},
                {
                    "label": "Highest risk",
                    "value": (
                        f"{low_attendance[0]['student']} ({low_attendance[0]['percentage']}%)"
                        if low_attendance
                        else "No low-attendance students"
                    ),
                },
            ],
        },
        {
            "title": "Performance insights",
            "action": {"label": "Upload results", "path": "/admin/exams"},
            "items": [
                {
                    "label": "Weakest performer",
                    "value": (
                        f"{weakest[0]['student']} ({weakest[0]['average_marks']})"
                        if weakest
                        else "No result records yet"
                    ),
                },
                {
                    "label": "Strongest performer",
                    "value": (
                        f"{strongest[0]['student']} ({strongest[0]['average_marks']})"
                        if strongest
                        else "No result records yet"
                    ),
                },
            ],
        },
    ]
    return {
        "headline": headline,
        "summary": summary,
        "sections": sections,
        "suggested_prompts": [
            "Which students have low attendance?",
            "Give me performance insights",
            "Generate test questions",
        ],
    }


def _build_admin_briefing(context):
    if "platform" in context:
        platform = context["platform"]
        return {
            "headline": "Platform automation brief",
            "summary": (
                f"The platform currently has {platform['institutions']} institutions, "
                f"{platform['students']} students, and {platform['teachers']} teachers."
            ),
            "sections": [
                {
                    "title": "Platform totals",
                    "action": {"label": "Open dashboard", "path": "/super-admin/dashboard"},
                    "items": [
                        {"label": "Institutions", "value": str(platform["institutions"])},
                        {"label": "Students", "value": str(platform["students"])},
                        {"label": "Teachers", "value": str(platform["teachers"])},
                    ],
                }
            ],
            "suggested_prompts": [
                "Give me a platform summary",
                "Show institution-level trends",
                "Summarize growth signals",
            ],
        }

    revenue = context["revenue"]
    admissions = context["admissions"]
    approvals = context["approvals"]
    announcements = context["recent_announcements"]

    headline = f"{context['institution']['name']} automation brief"
    summary = (
        f"Pending fees stand at {revenue['pending_amount']}, with {revenue['open_invoices']} open invoices, "
        f"{len(admissions)} admission status groups, and {len(approvals)} approval status groups."
    )
    sections = [
        {
            "title": "Revenue",
            "action": {"label": "Open fees", "path": "/admin/fees"},
            "items": [
                {"label": "Invoiced", "value": _format_currency(revenue["total_invoiced"])},
                {"label": "Collected", "value": _format_currency(revenue["total_paid"])},
                {"label": "Pending", "value": _format_currency(revenue["pending_amount"])},
                {"label": "Open invoices", "value": str(revenue["open_invoices"])},
            ],
        },
        {
            "title": "Admissions",
            "action": {"label": "Open admissions", "path": "/admin/admissions"},
            "items": [
                {"label": row["status"].title(), "value": str(row["count"])}
                for row in admissions
            ]
            or [{"label": "Status", "value": "No admissions yet"}],
        },
        {
            "title": "Approvals",
            "action": {"label": "Open approvals", "path": "/admin/approvals"},
            "items": [
                {"label": row["status"].title(), "value": str(row["count"])}
                for row in approvals
            ]
            or [{"label": "Status", "value": "No approval requests yet"}],
        },
        {
            "title": "Announcements",
            "action": {"label": "Open dashboard", "path": "/admin/dashboard"},
            "items": [
                {"label": "Recent posts", "value": str(len(announcements))},
                {
                    "label": "Latest",
                    "value": announcements[0]["title"] if announcements else "No announcements yet",
                },
            ],
        },
    ]
    return {
        "headline": headline,
        "summary": summary,
        "sections": sections,
        "suggested_prompts": [
            "Generate fee summary",
            "Show admission analytics",
            "Draft an announcement",
        ],
    }


def build_automation_briefing(user):
    role_context, _, context = build_role_context(user)
    if role_context == AIChat.ROLE_STUDENT:
        payload = _build_student_briefing(context)
    elif role_context == AIChat.ROLE_TEACHER:
        payload = _build_teacher_briefing(context)
    else:
        payload = _build_admin_briefing(context)
    payload["role_context"] = role_context
    return payload


def _openai_system_prompt(role_context):
    role_instruction = {
        AIChat.ROLE_STUDENT: (
            "You are a student assistant for a student management system. Focus on attendance, results, timetable, "
            "announcements, and study help. If assignment data is unavailable, say that clearly."
        ),
        AIChat.ROLE_TEACHER: (
            "You are a teacher assistant for a student management system. Focus on student analytics, low attendance, "
            "performance insights, and test-question drafting."
        ),
        AIChat.ROLE_ADMIN: (
            "You are an admin assistant for a student management system. Focus on revenue, admissions, approvals, "
            "announcement drafting, and operational summaries. If complaints are requested but unavailable, say so."
        ),
    }[role_context]
    return (
        f"{role_instruction} Use only the supplied database context as factual ground truth. "
        "Do not invent metrics, records, or modules. Keep answers concise, useful, and dashboard-friendly."
    )


def _call_openai(message, role_context, context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    api_url = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/responses")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    payload = {
        "model": model_name,
        "instructions": _openai_system_prompt(role_context),
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Database context:\n{context}\n\nUser request:\n{message}",
                    }
                ],
            }
        ],
        "max_output_tokens": int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "500")),
    }
    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    output_text = data.get("output_text")
    if output_text:
        return output_text.strip(), model_name

    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                parts.append(text)
    if not parts:
        raise RuntimeError("OpenAI response did not include text output.")
    return "\n".join(parts).strip(), model_name


def generate_ai_reply(user, message):
    role_context, institution, context = build_role_context(user)
    metadata = {
        "institution_id": getattr(institution, "id", None),
        "used_live_data": True,
    }
    try:
        reply, model_name = _call_openai(message, role_context, context)
        provider = AIChat.PROVIDER_OPENAI
        metadata["fallback_reason"] = ""
    except Exception as exc:
        reply = build_fallback_reply(role_context, message, context)
        model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        provider = AIChat.PROVIDER_FALLBACK
        metadata["fallback_reason"] = str(exc)

    chat = AIChat.objects.create(
        institution=institution,
        user=user,
        role_context=role_context,
        message=message,
        response=reply,
        context_snapshot=context,
        metadata=metadata,
        provider=provider,
        model_name=model_name,
    )
    return chat
