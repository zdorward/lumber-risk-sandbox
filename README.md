# Lumber Risk Sandbox

<img width="1512" height="851" alt="image" src="https://github.com/user-attachments/assets/744299eb-818d-4753-bc6d-acdfbfbbf7b8" />
<img width="1512" height="853" alt="image" src="https://github.com/user-attachments/assets/5860c32e-b0e9-45de-aec3-d93663c88d46" />


This project provides a demo environment for a lumber futures hedging model, complete with:

- A FastAPI backend (`app/api.py`)
- A Streamlit dashboard (`dashboard/app.py`)
- An ETL process to load historical lumber data (`app/etl.py`)
- Optional Docker environment for one‑command demos

---

## 🚀 Quickstart (Local)

### 1. Clone the repo

```bash
git clone https://github.com/zdorward/lumber-risk-sandbox.git lumber-risk-sandbox
cd lumber-risk-sandbox
```

### 2. Create & activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
make install
```

### 4. Run the full demo (backend + frontend)

```bash
make demo
```

Then open:

```
http://localhost:8501
```

You should see the analytics dashboard and be able to run hedge simulations.

---

## 🐳 Docker Quickstart

Prereqs:

- Docker installed
- Docker Desktop running

### 1. Clone the repo

```bash
git clone <repo-url> lumber-risk-sandbox
cd lumber-risk-sandbox
```

### 2. Start the entire environment

```bash
docker compose up --build
```

This builds the project image and launches:

- **Backend** → http://localhost:8000
- **Dashboard** → http://localhost:8501

### 3. Stop everything

In the same terminal:

```bash
CTRL+C
docker compose down
```

---

## 🧪 Testing the Backend Directly

After starting Docker or `make backend`, verify the API:

```
http://localhost:8000/docs
```

Or test analytics:

```bash
curl "http://localhost:8000/analytics?symbol=LBS=F&short_window=10&long_window=30&notional=100000"
```

---

## 📁 Project Structure Overview

```
lumber-risk-sandbox/
│
├── app/
│   ├── api.py          # FastAPI backend
│   ├── etl.py          # Loads historical data
│   ├── analytics.py    # Hedge analytics engine
│   └── models.py       # DB models
│
├── dashboard/
│   └── app.py          # Streamlit UI
│
├── lumber.db           # Created by ETL (not versioned)
├── makefile            # Local commands (demo, backend, frontend)
├── Dockerfile
├── docker-compose.yml
└── README.md
```
