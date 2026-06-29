from __future__ import annotations

from flask import Blueprint, jsonify, request

from .db import fetch_account_by_email


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    account = fetch_account_by_email(email)
    if not account:
        return jsonify({"error": "Invalid credentials."}), 401

    if account["status"] != "active":
        return jsonify({"error": "Account is disabled."}), 403

    if password != account["password_hash"]:
        return jsonify({"error": "Invalid credentials."}), 401

    return jsonify(
        {
            "id": account["id"],
            "email": account["email"],
            "full_name": account["full_name"],
            "role": account["role"],
        }
    ), 200