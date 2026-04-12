# 🚨 RapidAid — Emergency First Aid Web Application

A full-stack emergency first aid web application built with **Python Flask**, **SQLite/MySQL**, and **Vanilla JS**. Provides instant, AI-assisted first aid guidance with multilingual support, emergency calling, contact management, and panic mode.

---

## 📁 Project Structure

```
rapidaid/
├── app.py                    # Main Flask application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore
│
├── database/
│   ├── __init__.py
│   ├── db.py                 # Database connection & initialization
│   └── schema.sql            # SQL table definitions (SQLite + MySQL)
│
├── routes/
│   ├── __init__.py
│   ├── auth.py               # Register / Login / Logout / Session
│   ├── contacts.py           # Emergency contacts CRUD
│   ├── firstaid.py           # First aid instructions (EN / HI / MR)
│   ├── history.py            # First aid session history
│   └── ai_guide.py           # Claude AI-assisted guidance endpoint
│
├── templates/
│   ├── index.html            # Main SPA template (Jinja2)
│   ├── 404.html              # Not found page
│   └── 500.html              # Server error page
│
├── static/
│   ├── css/
│   │   └── style.css         # Full UI stylesheet (dark minimalist)
│   └── js/
│       ├── translations.js   # EN / HI / MR UI strings
│       ├── api.js            # Backend API helper functions
│       └── app.js            # Main application logic
│
└── instance/
    └── rapidaid.db           # SQLite database (auto-created on run)
```

---

## ✅ Features

### Without Login
| Feature | Description |
|---|---|
| Emergency Type Selection | Burns, Bleeding, Fracture, Choking, Heart Attack, Drowning |
| Step-by-step First Aid | Detailed instructions per emergency type |
| AI-Assisted Guidance | Claude API generates contextual advice |
| One-Tap Emergency Call | 108 Ambulance, 100 Police, 101 Fire |
| Multilingual Support | English, Hindi (हिन्दी), Marathi (मराठी) |

### Login Required
| Feature | Description |
|---|---|
| Save Emergency Contacts | Up to 10 family/friend contacts |
| Panic Mode | One tap alerts all contacts + suggests 108 |
| First Aid History | Track all past emergency sessions |

---

## 🚀 Setup & Run

### 1. Clone / Download
```bash
git clone <your-repo-url>
cd rapidaid
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 5. Run the App
```bash
python app.py
```
Open browser: **http://localhost:5000**

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create account | ❌ |
| POST | `/auth/login` | Login | ❌ |
| POST | `/auth/logout` | Logout | ✅ |
| GET  | `/auth/me` | Session check | ❌ |

### First Aid
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/firstaid/<lang>/<type>` | Get instructions | ❌ |
| GET | `/firstaid/types` | List all types | ❌ |

### Contacts
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/contacts/` | Get all contacts | ✅ |
| POST | `/contacts/add` | Add contact | ✅ |
| DELETE | `/contacts/delete/<id>` | Remove contact | ✅ |

### History
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/history/` | Get history | ✅ |
| DELETE | `/history/clear` | Clear history | ✅ |

### AI & Panic
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/ai/guide` | AI first aid guidance | ❌ |
| POST | `/panic` | Trigger panic mode | ✅ |

---

## 🗄️ Database

**Development**: SQLite (auto-created at `instance/rapidaid.db`)

**Production (MySQL)**:
```sql
CREATE DATABASE rapidaid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then update `DATABASE_URL` in `.env` and modify `database/db.py` to use `PyMySQL`.

Schema tables: `users`, `contacts`, `history` — see `database/schema.sql`

---

## 🤖 AI Integration

Uses **Anthropic Claude API** (`claude-haiku`) for AI-assisted guidance.

Get your free API key: https://console.anthropic.com

Without an API key, the app still works fully — it uses the built-in static first aid data.

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.10+, Flask 3.0 |
| Database | SQLite (dev) / MySQL (prod) |
| AI | Anthropic Claude API (claude-haiku) |
| Auth | Flask sessions + bcrypt password hashing |
| Fonts | Syne (headings), DM Sans (body) via Google Fonts |

---

## 🌐 Multilingual Support

Instructions available in:
- 🇬🇧 **English** (en)
- 🇮🇳 **Hindi** (hi) — हिन्दी
- 🇮🇳 **Marathi** (mr) — मराठी

---

## 📱 Emergency Numbers (India)

| Service | Number |
|---|---|
| Ambulance | 108 / 112 |
| Police | 100 |
| Fire Brigade | 101 |

---

## 👨‍💻 Team / Submission Info

- **Project**: RapidAid Emergency First Aid System
- **Phase**: Phase 1 — Core System
- **Semester**: Current Semester
- **Stack**: HTML + CSS + JS + Python Flask + SQLite/MySQL + Claude AI

---

## 📄 License

For academic/educational use. Not for commercial deployment without proper medical review.
