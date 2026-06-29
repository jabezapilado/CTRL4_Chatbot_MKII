# SOC Guidance Office Chatbot — Frontend
Holy Angel University | School of Computing
AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

## Current State

- The frontend is now wired to the Flask backend in this workspace.
- `login.html` routes `student` to the chatbot page and `staff` / `admin` to the dashboard.
- `dashboard.js` consumes backend inquiry, appointment, settings, and account endpoints.
- `chat.js` sends messages to the live `/chat` route.
- `chat_admin.js` still keeps some takeover/session state in the browser for now.

## Prototype Login

Use these seeded local accounts when testing the login page:

- `student@hau.edu.ph` / `student123`
- `staff@hau.edu.ph` / `staff123`
- `admin@hau.edu.ph` / `admin123`

## Tech Stack

- HTML5
- CSS3 with custom properties, flexbox, grid, and responsive layouts
- Vanilla JavaScript
- Flask backend serving the templates and static assets

## Folder Structure

```
frontend/
│
├── templates/
│   ├── appointment.html   ← Student appointment booking page
│   ├── chatbot.html       ← Student-facing chat interface
│   ├── chatbot_admin.html ← Admin helper/chat takeover page
│   ├── dashboard.html     ← Staff/Admin inquiry dashboard
│   └── login.html         ← Login page for staff and students
│
├── static/
│   ├── css/
│   │   ├── appointment.css ← Styles for appointment.html
│   │   ├── base.css        ← Shared variables, reset, badges, buttons
│   │   ├── chatbot.css     ← Styles for chatbot.html
│   │   ├── dashboard.css   ← Styles for dashboard.html
│   │   └── login.css       ← Styles for login.html
│   │
│   ├── img/
│   └── js/
│       ├── appointment.js ← Appointment form and modal interactions
│       ├── auth.js        ← Login page behavior and logout support
│       ├── chat.js        ← Student chat logic
│       ├── chat_admin.js  ← Admin takeover helper logic
│       └── dashboard.js   ← Backend-driven dashboard logic
│
└── README.md
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
- Role-aware login for student, staff, and admin accounts
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

