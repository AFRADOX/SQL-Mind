# SQL-Mind 🧠

> A production-ready Text-to-SQL SaaS platform that converts plain English 
> questions into optimized PostgreSQL queries using LLaMA 3.3 AI. Features 
> JWT authentication, encrypted database connections, AST-based SQL validation, 
> 3-signal confidence scoring, and real-time query execution with a modern dark dashboard.

---

## 🚀 Features

- 🔐 **JWT Authentication** — Secure register/login system
- 🗄️ **Database Connection Management** — Connect any PostgreSQL database securely
- 🤖 **AI-Powered SQL Generation** — LLaMA 3.3 (via Groq API) converts English to SQL
- ✅ **SQL Validation** — AST-based parser blocks all non-SELECT statements
- 📊 **3-Signal Confidence Scoring** — HIGH / MEDIUM / LOW confidence badge
- 📝 **Query History** — Every query saved with results and confidence score
- 🎨 **Dark Premium UI** — Built with React.js + Tailwind CSS

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic (migrations) |
| AI Engine | Groq API, LLaMA 3.3 70B Versatile |
| SQL Validation | sqlglot (AST parsing) |
| Frontend | React.js, Tailwind CSS, Zustand |
| Authentication | JWT, Bcrypt, Fernet encryption |
| Architecture | Repository Pattern, Service Layer |

---
## 🏗️ How It Works

```
┌─────────────────────────────────────────┐
│           USER (Browser)                │
│   Types: "Show top 5 customers"         │
└──────────────┬──────────────────────────┘
               │ HTTP Request
               ▼
┌─────────────────────────────────────────┐
│         REACT FRONTEND                  │
│   (localhost:5173)                      │
│   Shows UI, sends request to backend    │
└──────────────┬──────────────────────────┘
               │ API Call
               ▼
┌─────────────────────────────────────────┐
│         FASTAPI BACKEND                 │
│   (localhost:8000)                      │
│                                         │
│   Step 1: Verify JWT token              │
│   Step 2: Read database schema          │
│   Step 3: Build prompt for AI           │
│   Step 4: Call Groq AI (LLaMA 3.3)      │
│   Step 5: Validate SQL (SELECT only)    │
│   Step 6: Run SQL on user's database    │
│   Step 7: Calculate confidence score    │
│   Step 8: Save to history               │
│   Step 9: Return results to frontend    │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────┐    ┌──────────────┐
│ Groq AI  │    │  PostgreSQL  │
│ LLaMA 3.3│    │  Database    │
│ Generates│    │  Stores:     │
│ the SQL  │    │  - Users     │
└──────────┘    │  - Connections│
                │  - History   │
                └──────────────┘
```
