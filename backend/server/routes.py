"""
Application Routes

Defines all frontend pages and REST API endpoints
for the CTRL4 Chatbot MK2.

Responsibilities

- Authentication
- Chat Processing
- Inquiry Management
- Appointment Management
- Dashboard APIs
- AI Integration
- Health Monitoring

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import logging

# from flask import Blueprint, jsonify, request
from flask import Blueprint, jsonify, request, render_template, redirect, session

from .db import fetch_rows, list_accounts, load_settings, save_appointment, save_escalation, save_inquiry, save_inquiry_manual, save_settings, update_appointment_status, update_inquiry_staff_notes, update_inquiry_status, utc_now

from .services import (
    ai_service,
    get_service_status,
)

logger = logging.getLogger(__name__)

CATEGORY_AI_CHAT = "ai_chat"
CATEGORY_MANUAL = "manual"
ESCALATION_STATUS_OPEN = "open"

api_bp = Blueprint("api", __name__)


def _get_logged_in_user():
    user = session.get("hau_user")
    return user if isinstance(user, dict) and user.get("email") else None


def _role_landing_path(user: dict) -> str:
    role = str(user.get("role", "student")).lower()
    if role in {"staff", "admin"}:
        return "/dashboard"
    return "/chatbot"


@api_bp.before_request
def require_login_for_private_routes():
    public_paths = {"/", "/login", "/health", "/auth/login", "/auth/logout"}
    path = request.path

    if path.startswith("/static/") or path in public_paths:
        if path in {"/", "/login"} and _get_logged_in_user():
            return redirect(_role_landing_path(_get_logged_in_user()))
        return None

    user = _get_logged_in_user()
    if not user:
        if path.startswith("/api/") or path == "/chat":
            return jsonify({"error": "Login required."}), 401
        return redirect("/login?reason=session-required")

    role = str(user.get("role", "student")).lower()
    if path in {"/chatbot", "/appointment"} and role in {"staff", "admin"}:
        return redirect("/dashboard")
    if path in {"/dashboard", "/chatbot_admin"} and role == "student":
        return redirect("/chatbot")

    return None

#==========================================
#Frontend routes
@api_bp.get("/")
def home():
    return render_template("login.html")


@api_bp.get("/login")
def login():
    return render_template("login.html")


@api_bp.get("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@api_bp.get("/appointment")
def appointment():
    return render_template("appointment.html")


@api_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@api_bp.get("/chatbot_admin")
def chatbot_admin():
    return render_template("chatbot_admin.html")

#==========================================

@api_bp.get("/health")
def health():

    return jsonify(
        get_service_status()
    ), 200


@api_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    result = ai_service.respond(

        message=message,

        conversation=payload.get(
            "conversation",
            [],
        ),

    )
    print("=" * 60)
    print("AIService returned:")
    print("SUCCESS:", result.success)
    print("RESPONSE:", result.response)
    print("EMOTION:", result.emotion)
    print("SENTIMENT:", result.sentiment)
    print("LANGUAGE:", result.language)
    print("ESCALATED:", result.escalated)
    print("CONFIDENCE:", result.confidence)
    print("=" * 60)
    
    if not result.success:

        logger.warning(
            "AIService failed for message: %s",
            message,
        )

        return jsonify({

            "success": False,

            "response": result.response,

        }), 200

    inquiry_id = save_inquiry(
        {
            "message": message,
            "response": result.response,
            "emotion": result.emotion,
            "escalate": result.escalated,
            "category": CATEGORY_AI_CHAT,
            "created_at": utc_now(),
        }
    )

    if result.escalated:
        save_escalation(
            {
                "inquiry_id": inquiry_id,
                "user_name": payload.get("user_name"),
                "user_email": payload.get("user_email"),
                "message": message,
                "conversation_json": payload.get("conversation", []),
                "status": ESCALATION_STATUS_OPEN,
                "created_at": utc_now(),
            }
        )

    return jsonify({

        "success": result.success,

        "response": result.response,

        "emotion": result.emotion,

        "sentiment": result.sentiment,

        "language": result.language,

        "escalated": result.escalated,

        "confidence": round(
            result.confidence,
            4,
        ),

    }), 200


@api_bp.get("/api/inquiries")
def inquiries():
    return jsonify({"items": fetch_rows("SELECT * FROM inquiries ORDER BY id DESC LIMIT 100")}), 200


@api_bp.get("/api/escalations")
def escalations():
    return jsonify({"items": fetch_rows("SELECT * FROM escalations ORDER BY id DESC LIMIT 100")}), 200


@api_bp.get("/api/appointments")
def appointments():
    return jsonify({"items": fetch_rows("SELECT * FROM appointments ORDER BY id DESC LIMIT 100")}), 200


@api_bp.get("/api/accounts")
def accounts():
    return jsonify({"items": list_accounts()}), 200


@api_bp.get("/api/settings")
def settings():
    return jsonify(load_settings()), 200


@api_bp.post("/api/settings")
def update_settings():
    payload = request.get_json(silent=True) or {}
    save_settings(payload)
    return jsonify({"status": "saved"}), 200


@api_bp.post("/api/appointments")
def create_appointment():
    payload = request.get_json(silent=True) or {}
    required_fields = ["student_name", "preferred_date", "preferred_time", "reason"]
    missing_fields = [field for field in required_fields if not str(payload.get(field, "")).strip()]

    if missing_fields:
        return jsonify({"error": "Missing required fields.", "fields": missing_fields}), 400

    appointment_id = save_appointment(
        {
            "student_name": payload["student_name"],
            "student_email": payload.get("student_email"),
            "preferred_date": payload["preferred_date"],
            "preferred_time": payload["preferred_time"],
            "reason": payload["reason"],
            "status": payload.get("status", "pending"),
            "created_at": utc_now(),
        }
    )

    return jsonify({"id": appointment_id, "status": "saved"}), 201

@api_bp.post("/api/inquiries")
def create_inquiry():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Missing required fields.", "fields": ["message"]}), 400

    result = ai_service.respond(

        message=message,

        conversation=payload.get(
            "conversation",
            [],
        ),

    )
    if not result.success:

        logger.warning(
            "AIService failed while creating manual inquiry: %s",
            message,
        )

        return jsonify({

            "success": False,

            "response": result.response,

        }), 200

    inquiry_id = save_inquiry_manual(
        {
            "student_id": payload.get("student_id"),
            "student_name": payload.get("student_name"),
            "student_email": payload.get("student_email"),
            "message": message,
            "response": result.response,
            "emotion": result.emotion,
            "escalate": result.escalated,
            "status": payload.get("status", "pending"),
            "category": payload.get(
                "category",
                CATEGORY_MANUAL,
            ),
            "staff_notes": payload.get("staff_notes"),
            "created_at": utc_now(),
        }
    )

    return jsonify({"id": inquiry_id, "status": "saved"}), 201

@api_bp.patch("/api/inquiries/<int:inquiry_id>")
def change_inquiry(inquiry_id: int):
    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip() or "pending"
    staff_notes = payload.get("staff_notes")
    update_inquiry_status(inquiry_id, status, staff_notes)
    if staff_notes:
        update_inquiry_staff_notes(inquiry_id, staff_notes)
    return jsonify({"status": "updated"}), 200

@api_bp.patch("/api/appointments/<int:appointment_id>")
def change_appointment(appointment_id: int):
    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip() or "pending"
    student_name = payload.get("student_name")
    update_appointment_status(appointment_id, status, student_name)
    return jsonify({"status": "updated"}), 200