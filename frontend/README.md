# SOC Guidance Office Chatbot — Frontend
Holy Angel University | School of Computing
Development of an AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

## Current State

- The frontend is now wired to the Flask backend in this workspace.
- `login.html` routes `student` to the chatbot page and `staff` / `admin` to the dashboard.
- `dashboard.js` consumes backend inquiry, appointment, settings, and account endpoints.
- `chat.js` sends messages to the live `/chat` route.
- `chat_admin.js` still keeps some takeover/session state in the browser for now.
- Chat responses are now grounded by the backend multilingual RAG service.
- The backend also runs NLP-based negative emotion detection and may escalate counselor support immediately.

## Prototype Login

Use school-issued accounts, or configure local seed accounts through backend `.env` values.

## Tech Stack

- HTML5
- CSS3 with custom properties, flexbox, grid, and responsive layouts
- Vanilla JavaScript
- Flask backend serving the templates and static assets

## Project Structure

```text
frontend/
├─ README.md
├─ templates/
│  ├─ appointment.html
│  ├─ chatbot.html
│  ├─ chatbot_admin.html
│  ├─ dashboard.html
│  └─ login.html
└─ static/
	├─ css/
	│  ├─ appointment.css
	│  ├─ base.css
	│  ├─ chatbot.css
	│  ├─ dashboard.css
	│  └─ login.css
	├─ img/
	└─ js/
		├─ appointment.js
		├─ auth.js
		├─ chat.js
		├─ chat_admin.js
		└─ dashboard.js
```

## Page Overview

### 1. `appointment.html` - Student Appointment Booking
- Request form for guidance counseling appointments
- Validation and success modal feedback
- Holy Angel University branding

### 2. `chatbot.html` - Student Chat Interface
- Brand-themed chat window
- Quick reply buttons for common inquiries
- Typing indicator animation
- Emotion badge per bot response
- Escalation notice when a message is flagged

### 3. `dashboard.html` - Staff/Admin Dashboard
- Sidebar navigation and summary cards
- Filterable inquiry and appointment lists
- Backend-driven status updates and notes
- Mobile-responsive collapsible sidebar

### 4. `login.html` - Login Page
- Account-based login for student, staff, and admin accounts
- Email and password fields with validation states
- Backend login call to `/auth/login`

## How to Run

1. Open the project's backend folder.
2. Activate the project-local virtual environment.
3. Start the Flask backend.

```bash
cd backend
source .venv/bin/activate
python app.py
```

4. Open the frontend through the Flask app so templates and static files load correctly.

## Backend Contract

- Chat messages go to `/chat`.
- Authentication goes to `/auth/login`.
- Dashboard data comes from `/api/inquiries`, `/api/escalations`, `/api/appointments`, `/api/accounts`, and `/api/settings`.
- The backend returns JSON responses that the frontend renders directly.

## AI Integration Note

- The frontend does not read from the top-level `ai/` folder.
- The active chatbot behavior comes from backend RAG components (`backend/server/service.py`, `backend/knowledge_base/`, and `backend/data/rag_index/`).
- The top-level `ai/` folder is retained as legacy archive only.

## Color Theme
| Name | Hex | Use |
|------|-----|-----|
| Maroon | `#7B1113` | Primary brand color |
| Maroon Dark | `#5A0C0E` | Header gradient, hover states |
| Gold | `#C9A84C` | Accents, borders |
| Gold Light | `#E8C97A` | Highlights on dark backgrounds |

## Notes

- This frontend is designed to live inside the Flask project root.
- Staff and admin currently share the same dashboard page.
- The admin helper page still keeps some browser-side takeover state until that flow is fully backend-backed.

