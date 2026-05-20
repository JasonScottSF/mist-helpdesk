# Mist Helpdesk

A guided troubleshooting tool for Tier 1 / Tier 2 helpdesk technicians working on Juniper Mist networks.

Authenticates against the Mist API and walks the tech through a step-by-step wizard — collecting the issue, reporter, site, and affected client — then serves up runbook-matched Marvis query cards pre-filled with the right names. Results are compiled into a structured escalation note you can paste straight into your ticketing system.

---

## Features

- **Mist SSO login** — authenticates against your Mist org; supports MFA and multi-org accounts
- **Guided wizard** — one question at a time, no Mist portal knowledge required
- **Runbook-driven queries** — maps 11 issue categories (wireless, switching, end-to-end) to the right Marvis prompts, pre-filled with client and site names
- **Searchable client picker** — live list of currently connected wireless and wired clients, filterable by name, username, MAC, or IP
- **One-click Marvis queries** — run suggested queries and check which results to include in notes
- **Ticket notes generator** — structured escalation notes ready to copy into your ticketing system

---

## Quick start

### Prerequisites
- Docker + Docker Compose

### Run

```bash
git clone https://github.com/JasonScottSF/mist-helpdesk.git
cd mist-helpdesk
cp .env.example .env
docker compose up --build
```

Open **http://localhost:5004** and sign in with your Mist credentials.

### Ports

| Service  | Default |
|----------|---------|
| Web UI   | 5004    |

Change the port by setting `PORT=XXXX` in your `.env` file.

---

## Configuration

Copy `.env.example` to `.env` and adjust as needed:

| Variable    | Default                      | Description                                                   |
|-------------|------------------------------|---------------------------------------------------------------|
| `PORT`      | `5004`                       | Host port the web UI binds to                                 |
| `SECRET_KEY`| `change-me-in-production`    | Random string used to sign session tokens — **change this**   |
| `MIST_BASE` | `https://api.mist.com`       | Regional Mist API base. Options: `api.eu.mist.com`, `api.gc1.mist.com` |
| `SESSION_TTL`| `28800`                     | Session lifetime in seconds (default 8 h)                     |

---

## Architecture

Three Docker services, all on an internal bridge network:

```
Browser → nginx (frontend, :5004)
              └── /api/* → FastAPI (api, :8000)
                               └── Mist Cloud API
                               └── Redis (sessions)
```

| Service    | Stack              | Purpose                                              |
|------------|--------------------|------------------------------------------------------|
| `frontend` | React + Vite + nginx | UI wizard, served as static files                   |
| `api`      | Python / FastAPI   | Mist API proxy, session management, runbook logic    |
| `redis`    | Redis 7            | Server-side session store (Mist cookies never reach browser) |

Session security: the Mist cookie jar is serialised into Redis and never forwarded to the browser. The browser only holds an `httpOnly` session UUID cookie issued by the API.

---

## Troubleshooting flows covered

Based on three Marvis runbooks:

| Runbook | Issues |
|---------|--------|
| **01 — Wireless** | Can't connect, slow Wi-Fi / call drops, auth failures, connected-no-traffic, scope check |
| **02 — Switching** | Dead desk port, PoE failure, switch/closet down, wrong VLAN, port speed issues |
| **03 — End-to-End** | Site-wide outage, SSO/RADIUS broken, slow on both wired and Wi-Fi, guest/IoT SSID, WAN |

---

## Development

### Frontend (hot-reload)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 — proxies /api to localhost:8000
```

### API (with Redis)

```bash
# Start just Redis
docker compose up redis -d

# Install deps and run
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Project layout

```
mist-helpdesk/
├── docker-compose.yml
├── .env.example
├── api/
│   ├── main.py              # FastAPI app
│   ├── mist_client.py       # Mist API wrapper (requests.Session)
│   ├── session_store.py     # Redis session management
│   ├── runbooks.py          # Query suggestions by issue category
│   └── routers/
│       ├── auth.py          # Login, MFA, org selection, logout
│       ├── sites.py         # Site list
│       ├── clients.py       # Wireless + wired client lists
│       └── marvis.py        # Marvis query proxy + suggestions
└── frontend/
    └── src/
        ├── pages/           # Login, OrgPicker, Wizard
        └── components/
            ├── steps/       # Wizard steps (Issue → Reporter → Site → Client → Investigate → Notes)
            └── ui/          # SearchList, QueryCard
```

---

## Contributing

This repo requires pull requests — **no direct pushes to `main`**.

### Workflow

1. Fork or create a feature branch
   ```bash
   git checkout -b feat/my-change
   ```
2. Make your changes and commit
3. Push and open a pull request against `main`
4. One approving review is required before merge

> **Repo admins** can approve and merge their own pull requests without a second reviewer.

### Branch protection summary

| Rule | Setting |
|------|---------|
| Direct push to `main` | ❌ Blocked for non-admins |
| Pull request required | ✅ Yes |
| Required approvals | 1 |
| Admin bypass | ✅ Admins may approve and merge their own PRs |

---

## License

MIT
