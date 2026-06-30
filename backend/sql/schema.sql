CREATE DATABASE IF NOT EXISTS soc_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE soc_chatbot;

CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role ENUM('student', 'staff', 'admin') NOT NULL DEFAULT 'student',
    status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS inquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    emotion VARCHAR(20) NOT NULL,
    escalate TINYINT(1) NOT NULL DEFAULT 0,
    category VARCHAR(50) NOT NULL DEFAULT 'general',
    created_at DATETIME NOT NULL
);

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
);

CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    student_email VARCHAR(255) NULL,
    preferred_date DATE NOT NULL,
    preferred_time TIME NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Insert accounts manually with hashed passwords, or use backend/.env seeding variables with scripts/setup_database.py.
