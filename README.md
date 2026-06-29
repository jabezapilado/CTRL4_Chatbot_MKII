# AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

## Overview

- Web-based chatbot for student inquiries and guidance office support.
- Flask backend now serves live chat, login, dashboard, and database endpoints.
- Role-based routing is active: `student` goes to the chatbot page, while `staff` and `admin` go to the dashboard.
- Uses rule-based responses for routine questions and NLP-based negative emotion detection for escalation handling.
- This is the first working prototype build.

## Tech Stack

- **Python 3.10+** for the Flask backend and AI model service.
- **Flask** and **Flask-CORS** for API endpoints and local server execution.
- **MySQL / MariaDB** through XAMPP for local database storage.
- **HTML, CSS, JavaScript** for the frontend interface.
- **pandas**, **scikit-learn**, **mysql-connector-python**, and **python-dotenv** for the backend and AI layer.

## Prerequisites

Install or verify the following before running the project:

1. Python 3.10 or newer.
2. XAMPP with MySQL/MariaDB running locally.
3. A browser for opening the frontend pages.
4. Git, if you want to clone or manage the project through version control.

## Getting Started

1. Open the `CTRL4_Chatbot/` folder in your editor.
2. Open a terminal in `CTRL4_Chatbot/backend/`.
3. Create and activate the project-local virtual environment.
4. Install the backend dependencies.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Backend Workflow (Flask + XAMPP)

1. Start Apache and MySQL from the XAMPP Control Panel.
2. Make sure the database settings in `backend/.env` match your local setup.
3. Run the bootstrap script to install dependencies and seed the database.

```bash
cd backend
bash setup.sh
```

4. Start the Flask backend.

```bash
cd backend
source .venv/bin/activate
python app.py
```

5. Check the health endpoint if needed.

```bash
curl http://127.0.0.1:5000/health
```

6. The backend exposes `/chat`, `/auth/login`, `/api/inquiries`, `/api/escalations`, `/api/appointments`, `/api/accounts`, and `/api/settings`.

7. The seeded prototype accounts are:

```text
student@hau.edu.ph / student123
staff@hau.edu.ph / staff123
admin@hau.edu.ph / admin123
```

## Frontend Workflow

1. Open the HTML files inside `frontend/templates/`.
2. The frontend currently contains the chatbot, dashboard, login, appointment, and admin helper pages.
3. The login page already routes by role, and the dashboard now reads from backend endpoints.

## Example Commands

```bash
cd backend
bash setup.sh
python app.py
curl http://127.0.0.1:5000/health
```

## Project Structure

```text
CTRL4_Chatbot/
├─ README.md
├─ frontend/
│  ├─ README.md
│  ├─ templates/
│  │  ├─ appointment.html
│  │  ├─ chatbot.html
│  │  ├─ chatbot_admin.html
│  │  ├─ dashboard.html
│  │  └─ login.html
│  └─ static/
│     ├─ css/
│     ├─ img/
│     └─ js/
├─ backend/
│  ├─ README.md
│  ├─ app.py
│  ├─ server/
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ db.py
│  │  ├─ routes.py
│  │  └─ service.py
│  ├─ scripts/
│  │  └─ setup_database.py
│  ├─ sql/
│  │  └─ schema.sql
│  ├─ requirements.txt
│  ├─ setup.sh
│  └─ .env.example
└─ ai/
	├─ chatbot_ai.py
	├─ dataset.csv
	├─ english_stopwords.txt
	├─ goemotions_1.csv
	└─ tagalog_stopwords.txt
```

## Algorithms and Features

- Rule-based intent recognition for common inquiry replies.
- TF-IDF feature extraction for text preprocessing.
- Logistic Regression for negative emotion detection.
- Escalation logging for emotionally sensitive inquiries.
- Local MySQL/MariaDB storage through XAMPP.
- Seeded student, staff, and admin accounts for role-based access.

## Assumptions and Limitations

- The backend is intended to run locally with XAMPP during development.
- The chatbot currently relies on the existing GoEmotions dataset prototype.
- Staff and admin currently share the same dashboard page.
- The system focuses on English text-based student inquiries.

## Submission Checklist

- [x] Frontend folder structure organized
- [x] Flask backend scaffold created
- [x] XAMPP-compatible database schema added
- [x] AI model service connected to the existing dataset
- [x] README rewritten to match the usual project format
- [x] Frontend connected to live backend endpoints
- [x] XAMPP MySQL integration tested end to end
- [x] Browser flow validated for chat and escalation

## Contributors

- Apilado, Jabez Timothy E. - Back-end Lead, Integration, and QA
- Quilantang, Grant Mihkael D. - Front-end Lead
- Lanix, Iligan - AI Model Lead
- Wylengco, Teyshaun Zell - UI/UX Lead

## References

- Flask Documentation
- MySQL / MariaDB Documentation
- scikit-learn Documentation
- pandas Documentation

## License

This project is for educational use. Apply additional licensing as needed before redistribution.