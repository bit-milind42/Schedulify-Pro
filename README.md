# Schedulify Pro

>A lightweight, role-based scheduling & appointment booking platform built with Django 5, modern Bootstrap UI, and a clean, extensible architecture.

## ✨ Core Features
- Role-based accounts: Customer & Provider (custom user model)
- Provider specialties & search (username + specialty keyword)
- Availability windows → automatic slot generation
- Manual slot CRUD (with safeguards when booked)
- Multi-step booking wizard (Provider → Day → Slot → Confirm)
- Real‑time slot loading via AJAX (JSON endpoint)
- Appointment lifecycle: pending → approved/rejected/cancelled
- Provider actions (approve / reject); customer cancellation
- Email notifications (console backend in dev) for bookings & status changes
- Card‑driven dashboards with metrics & upcoming/past sections
- Responsive provider directory (card grid with specialty badges)
- Toast message system (Bootstrap toasts rendered from Django messages)
- Clean, modern theming (custom CSS variables + subtle gradients)

## 🗂 Data Model Overview
- `accounts.User`: role (customer/provider), optional `specialty`
- `bookings.Availability`: date + start/end + interval (minutes)
- `bookings.Slot`: generated or manual time segment (booked/free flag)
- `bookings.Appointment`: links customer ↔ slot (status + timestamps)

## 🚀 Quick Start
```pwsh
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Browse: http://127.0.0.1:8000/

## 🔑 Key URLs
| Purpose | Path |
|---------|------|
| Register | /accounts/register/ |
| Login | /accounts/login/ |
| Unified Dashboard | /accounts/dashboard/ |
| Provider Directory | /accounts/providers/ |
| Provider Slots (self) | /bookings/slots/ |
| Provider Slots (customer view) | /bookings/providers/<id>/slots/ |
| Appointments | /bookings/appointments/ |
| Admin | /admin/ |

## 📬 Email Notifications
Configured with Django console backend (prints to terminal). Swap `EMAIL_BACKEND` and add SMTP settings in `config/settings.py` for production.

## 🧭 Booking Flow (Wizard)
1. Select provider
2. Pick a day (AJAX fetches free slots)
3. Choose a slot card
4. Confirm → appointment created (pending)
5. Provider approves/rejects (emails fired)

## 🛠 Tech Notes
- Django 5.x, custom user model from project start
- Bootstrap 5 + custom `static/css/style.css` theme layer
- Messages serialized to JSON for safe toast hydration in `base.html`
- Search implemented with `Q` lookups across username & specialty
- Availability creation triggers slot generation (interval-based)

## 🔒 Production Hardening TODO (Not Implemented Yet)
- Rate limiting & throttling on booking endpoints
- Conflict prevention (double booking race conditions)
- Pagination for large provider & appointment lists
- Time zone personalization (currently UTC)
- Email delivery via real provider (SMTP / API)
- Audit logging & analytics

## 🧹 Dev Housekeeping
- SQLite dev database included in workflow (not for prod)
- Secret key hard-coded dev only: replace with env var in deployment
- Minimal form validation; extend for stricter business rules

## 🤝 Contributing
Fork, branch, and submit PRs. Suggested contribution areas: timezone support, pagination, ICS export, calendar integrations.

## 📄 License
Internal / educational prototype (add explicit license if distributing).

---
Built as a focused, extensible starter to accelerate scheduling products. Rename, extend, or integrate as needed.
