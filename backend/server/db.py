from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from typing import Any

import mysql.connector
from werkzeug.security import generate_password_hash

from .config import Config


config = Config()


def _connection_kwargs(database: str | None = None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "host": config.DB_HOST,
        "port": config.DB_PORT,
        "user": config.DB_USER,
        "password": config.DB_PASSWORD,
        "autocommit": False,
    }
    if database:
        kwargs["database"] = database

    ssl_options: dict[str, Any] = {}
    if config.DB_SSL_CA:
        ssl_options["ca"] = config.DB_SSL_CA
        ssl_options["verify_cert"] = config.DB_SSL_VERIFY_CERT
    if ssl_options:
        kwargs["ssl_ca"] = ssl_options.get("ca")
        kwargs["ssl_verify_cert"] = ssl_options.get("verify_cert", False)

    return kwargs


def _server_connection():
    return mysql.connector.connect(**_connection_kwargs())


def _database_connection():
    return mysql.connector.connect(**_connection_kwargs(config.DB_NAME))


def utc_now() -> datetime:
    return datetime.utcnow().replace(microsecond=0)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return value


def _json_safe_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _json_safe_value(value) for key, value in row.items()}


def _seed_accounts() -> list[tuple[str, str, str, str, str, datetime]]:
    accounts = [
        {
            "email": config.SEED_STUDENT_EMAIL,
            "full_name": config.SEED_STUDENT_NAME,
            "password": config.SEED_STUDENT_PASSWORD,
            "role": "student",
        },
        {
            "email": config.SEED_STAFF_EMAIL,
            "full_name": config.SEED_STAFF_NAME,
            "password": config.SEED_STAFF_PASSWORD,
            "role": "staff",
        },
        {
            "email": config.SEED_ADMIN_EMAIL,
            "full_name": config.SEED_ADMIN_NAME,
            "password": config.SEED_ADMIN_PASSWORD,
            "role": "admin",
        },
    ]

    rows: list[tuple[str, str, str, str, str, datetime]] = []
    for account in accounts:
        email = str(account["email"]).strip().lower()
        password = str(account["password"])
        full_name = str(account["full_name"]).strip()
        role = str(account["role"]).strip().lower()

        if not email or not password or not full_name:
            continue

        rows.append(
            (
                email,
                generate_password_hash(password),
                full_name,
                role,
                "active",
                utc_now(),
            )
        )

    return rows


def initialize_database() -> None:
    with _server_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET {config.DB_CHARSET} COLLATE {config.DB_CHARSET}_unicode_ci"
            )
        connection.commit()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    role ENUM('student', 'staff', 'admin') NOT NULL DEFAULT 'student',
                    status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
                    created_at DATETIME NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inquiries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(50) NULL,
                    user_name VARCHAR(255) NULL,
                    user_email VARCHAR(255) NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    emotion VARCHAR(20) NOT NULL,
                    escalate TINYINT(1) NOT NULL DEFAULT 0,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    category VARCHAR(50) NOT NULL DEFAULT 'general',
                    staff_notes TEXT NULL,
                    source VARCHAR(20) NOT NULL DEFAULT 'chatbot',
                    created_at DATETIME NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS escalations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    inquiry_id INT NULL,
                    user_name VARCHAR(255) NULL,
                    user_email VARCHAR(255) NULL,
                    message TEXT NOT NULL,
                    conversation_json JSON NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'open',
                    created_at DATETIME NOT NULL,
                    CONSTRAINT fk_escalations_inquiries
                        FOREIGN KEY (inquiry_id) REFERENCES inquiries(id)
                        ON DELETE SET NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_name VARCHAR(255) NOT NULL,
                    student_email VARCHAR(255) NULL,
                    preferred_date DATE NOT NULL,
                    preferred_time TIME NOT NULL,
                    reason TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    created_at DATETIME NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) NOT NULL UNIQUE,
                    setting_value TEXT NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )

            seed_rows = _seed_accounts()
            if seed_rows:
                cursor.executemany(
                    """
                    INSERT IGNORE INTO accounts (email, password_hash, full_name, role, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    seed_rows,
                )
        connection.commit()


def save_inquiry(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inquiries (student_id, user_name, user_email, message, response, emotion, escalate, status, category, staff_notes, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("student_id"),
                    payload.get("user_name"),
                    payload.get("user_email"),
                    payload["message"],
                    payload["response"],
                    payload["emotion"],
                    1 if payload.get("escalate") else 0,
                    payload.get("status", "pending"),
                    payload.get("category", "general"),
                    payload.get("staff_notes"),
                    payload.get("source", "chatbot"),
                    payload.get("created_at", utc_now()),
                ),
            )
            inquiry_id = cursor.lastrowid
        connection.commit()
        return int(inquiry_id)


def save_inquiry_manual(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inquiries (student_id, user_name, user_email, message, response, emotion, escalate, status, category, staff_notes, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("student_id"),
                    payload.get("student_name"),
                    payload.get("student_email"),
                    payload["message"],
                    payload["response"],
                    payload["emotion"],
                    1 if payload.get("escalate") else 0,
                    payload.get("status", "pending"),
                    payload.get("category", "general"),
                    payload.get("staff_notes"),
                    payload.get("source", "manual"),
                    payload.get("created_at", utc_now()),
                ),
            )
            inquiry_id = cursor.lastrowid
        connection.commit()
        return int(inquiry_id)


def save_escalation(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO escalations (
                    inquiry_id, user_name, user_email, message, conversation_json, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("inquiry_id"),
                    payload.get("user_name"),
                    payload.get("user_email"),
                    payload["message"],
                    json.dumps(payload.get("conversation_json", [])),
                    payload.get("status", "open"),
                    payload.get("created_at", utc_now()),
                ),
            )
            escalation_id = cursor.lastrowid
        connection.commit()
        return int(escalation_id)


def save_appointment(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO appointments (
                    student_name, student_email, preferred_date, preferred_time, reason, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload["student_name"],
                    payload.get("student_email"),
                    payload["preferred_date"],
                    payload["preferred_time"],
                    payload["reason"],
                    payload.get("status", "pending"),
                    payload.get("created_at", utc_now()),
                ),
            )
            appointment_id = cursor.lastrowid
        connection.commit()
        return int(appointment_id)


def fetch_account_by_email(email: str) -> dict[str, Any] | None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT id, email, password_hash, full_name, role, status, created_at FROM accounts WHERE email = %s LIMIT 1",
                (email,),
            )
            row = cursor.fetchone()
    return row


def list_accounts() -> list[dict[str, Any]]:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, email, full_name, role, status, created_at FROM accounts ORDER BY id ASC")
            rows = cursor.fetchall()
    return rows


def load_settings() -> dict[str, Any]:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM settings")
            rows = cursor.fetchall()

    settings = {
        "officeHours": "Monday to Friday, 8:00 AM - 5:00 PM",
        "officeEmail": "guidance@hau.edu.ph",
        "contactNumber": "(045) 123-4567",
        "officeLocation": "SOC Guidance Office, Holy Angel University",
        "autoFlag": True,
        "showSupport": False,
        "escalationMessage": "Your concern may need further attention from Guidance Office personnel. Please wait for proper assistance or contact the office directly if urgent.",
        "categories": [
            "Guidance Appointment",
            "Counseling Services",
            "Office Schedule",
            "Requirements and Procedures",
            "Emotional Support Concerns",
            "General Inquiry",
            "Unknown Inquiry",
        ],
        "faqs": [
            {
                "title": "Office Hours",
                "question": "What are your office hours?",
                "answer": "The SOC Guidance Office is open from Monday to Friday, 8:00 AM to 5:00 PM.",
            },
            {
                "title": "Book Appointment",
                "question": "How can I book an appointment?",
                "answer": "You may book an appointment by selecting the Book Appointment option and submitting your preferred date and reason for appointment.",
            },
            {
                "title": "Counseling Services",
                "question": "Can I speak with a counselor?",
                "answer": "Yes, you may request counseling assistance through the chatbot or visit the SOC Guidance Office during office hours.",
            },
        ],
    }

    for row in rows:
        key = row["setting_key"]
        value = row["setting_value"]
        if key in {"autoFlag", "showSupport"}:
            settings[key] = str(value).lower() in {"1", "true", "yes", "on"}
        elif key in {"categories", "faqs"}:
            try:
                settings[key] = json.loads(value)
            except json.JSONDecodeError:
                pass
        else:
            settings[key] = value

    return settings


def save_settings(settings: dict[str, Any]) -> None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            for key, value in settings.items():
                cursor.execute(
                    """
                    INSERT INTO settings (setting_key, setting_value, updated_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), updated_at = VALUES(updated_at)
                    """,
                    (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value), utc_now()),
                )
        connection.commit()


def fetch_rows(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
    return [_json_safe_row(row) for row in rows]


def update_inquiry_status(inquiry_id: int, status: str, staff_notes: str | None = None) -> None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE inquiries
                SET status = %s,
                    staff_notes = COALESCE(%s, staff_notes)
                WHERE id = %s
                """,
                (status, staff_notes, inquiry_id),
            )
        connection.commit()


def update_inquiry_staff_notes(inquiry_id: int, staff_notes: str) -> None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE inquiries SET staff_notes = %s WHERE id = %s",
                (staff_notes, inquiry_id),
            )
        connection.commit()


def update_appointment_status(appointment_id: int, status: str, student_name: str | None = None) -> None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE appointments
                SET status = %s,
                    student_name = COALESCE(%s, student_name)
                WHERE id = %s
                """,
                (status, student_name, appointment_id),
            )
        connection.commit()