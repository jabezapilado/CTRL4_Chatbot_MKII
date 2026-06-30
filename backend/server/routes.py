from __future__ import annotations

import json

# from flask import Blueprint, jsonify, request
from flask import Blueprint, jsonify, request, render_template

from .db import fetch_rows, list_accounts, load_settings, save_appointment, save_escalation, save_inquiry, save_inquiry_manual, save_settings, update_appointment_status, update_inquiry_staff_notes, update_inquiry_status, utc_now
from .service import get_chatbot_service


api_bp = Blueprint("api", __name__)

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
    return jsonify({"status": "ok", "model_ready": True}), 200


@api_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    service = get_chatbot_service()
    result = service.respond(message, conversation=payload.get("conversation", []))

    inquiry_id = save_inquiry(
        {
            "message": message,
            "response": result.response,
            "emotion": result.emotion,
            "escalate": result.escalate,
            "category": result.category,
            "created_at": utc_now(),
        }
    )

    if result.escalate:
        save_escalation(
            {
                "inquiry_id": inquiry_id,
                "user_name": payload.get("user_name"),
                "user_email": payload.get("user_email"),
                "message": message,
                "conversation_json": payload.get("conversation", []),
                "status": "open",
                "created_at": utc_now(),
            }
        )

    return jsonify(
        {
            "response": result.response,
            "emotion": result.emotion,
            "escalate": result.escalate,
            "category": result.category,
            "confidence": round(result.confidence, 4),
        }
    ), 200


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

    service = get_chatbot_service()
    result = service.respond(message)

    inquiry_id = save_inquiry_manual(
        {
            "student_id": payload.get("student_id"),
            "student_name": payload.get("student_name"),
            "student_email": payload.get("student_email"),
            "message": message,
            "response": result.response,
            "emotion": result.emotion,
            "escalate": result.escalate,
            "status": payload.get("status", "pending"),
            "category": payload.get("category", result.category),
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