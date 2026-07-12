# transiQ Backend

Flask API for the transiQ dashboard — login, JWT auth, and server-side RBAC
that mirrors the frontend's `roles.js` permissions.

## Setup

```bash
pip install -r requirements.txt
python3 app.py
```

Runs on `http://127.0.0.1:5000`. On first run it auto-creates `transiq.db`
(SQLite) and seeds it with demo users + fleet data.

## Demo accounts (password: `password`)

| Email                     | Role               |
|---------------------------|--------------------|
| manager@transiq.com       | Fleet Manager      |
| dispatch@transiq.com      | Dispatcher         |
| safety@transiq.com        | Safety Officer     |
| finance@transiq.com       | Financial Analyst  |

## Endpoints

- `POST /api/login` — `{ email, password, role }` → `{ token, email, name, role }`
- `GET /api/me` — decode current token
- `GET /api/dashboard/kpis` — role-specific KPI numbers
- `GET /api/vehicles` — Fleet Manager, Dispatcher only
- `GET /api/maintenance` — Fleet Manager only
- `GET /api/trips` — Dispatcher only
- `GET /api/drivers` — Safety Officer only
- `GET /api/reports` — Safety Officer, Financial Analyst
- `GET /api/expenses` — Financial Analyst only

All `GET` endpoints require `Authorization: Bearer <token>`. RBAC is enforced
server-side in `auth.py` (`ENDPOINT_ROLES`) — a valid token for one role gets
a 403 if it hits another role's endpoint, even if it knows the URL.

## Wiring up the frontend

In `login.html`, replace the `USERS` mock-lookup block with:

```js
const res = await fetch("http://127.0.0.1:5000/api/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password, role: selectedRole }),
});
const data = await res.json();
if (!res.ok) { showError(data.error); return; }
setSession({ role: data.role, name: data.name, token: data.token });
window.location.href = DASHBOARD_PAGE;
```

## Before production

- Set a real `SECRET_KEY` env var (don't use the dev default).
- Swap SQLite for Postgres via `DATABASE_URL`.
- Lock down `CORS(...)` to your actual frontend origin instead of `"*"`.
- Add a password-reset flow to unlock accounts (`user.locked`) — right now
  only a DB edit can clear it.
