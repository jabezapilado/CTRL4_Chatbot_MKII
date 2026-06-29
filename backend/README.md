# Backend

This folder contains the local Python backend for the chatbot.

## Structure

- `app.py` - entrypoint for local development
- `server/` - Flask package with app factory, blueprints, model service, and MySQL storage
- `scripts/setup_database.py` - seeds the database and default accounts
- `sql/schema.sql` - optional starter schema for XAMPP/phpMyAdmin
- `.env.example` - local database settings for XAMPP
- `.venv/` - project-local virtual environment created by `setup.sh`

## What it provides

- Flask API for chat inference at `/chat`
- Role-based login at `/auth/login`
- MySQL/MariaDB persistence that works with XAMPP
- Admin/staff endpoints for inquiries, escalations, appointments, accounts, and settings
- Local AI service that loads the existing GoEmotions training data

## Prototype Login

The first prototype uses seeded local accounts for testing:

- `student@hau.edu.ph` with password `student123`
- `staff@hau.edu.ph` with password `staff123`
- `admin@hau.edu.ph` with password `admin123`

The login endpoint compares the submitted password directly against the stored prototype value.

## Run locally

1. Start MySQL in XAMPP.
2. Make sure the database settings in `.env` match your local XAMPP configuration.
3. Run the bootstrap script from this folder.

```bash
cd backend
bash setup.sh
```

4. Start the app with `python app.py` from this folder.
5. Test `GET /health` and `POST /chat`.

If you want to run the setup steps manually instead of using the script:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/setup_database.py
```

## Notes

- The backend now expects MySQL/MariaDB instead of SQLite.
- The database setup script creates the database, tables, and default student/staff/admin accounts.
- The bootstrap script installs dependencies, creates the virtual environment if needed, and seeds the database.
- The frontend is already wired to the backend endpoints in this workspace.
- The backend reads `.env` with `python-dotenv`, so run it from the project-local virtual environment.