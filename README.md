
---

# Gestalt Question Review — Local Setup

## Prerequisites

* Git
* **Python ≥ 3.10**
* **Node.js ≥ 18** and npm

## 1) Clone the repo

```bash
git clone https://github.com/lucib3196/Gestalt_Question_Review.git
cd Gestalt_Question_Review
```

## 2) Environment variables

Create a `.env` file at the project root and add the secrets you were given.

> Tip: commit a `.env.example` (no secrets) so others know what keys to set.

## 3) Python virtual environment

```bash
python -m venv .venv
```

**Activate it**

* macOS/Linux:

  ```bash
  source .venv/bin/activate
  ```
* Windows (PowerShell):

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

## 4) Install backend requirements

```bash
pip install -r requirements.txt
```

## 5) Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## 6) Run the backend (FastAPI)

In one terminal (venv active):

```bash
uvicorn backend_api.main:app --reload
```

* API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 7) Run the frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

* App dev server (Vite/Next): the terminal will print the local URL (often `http://localhost:5173`).

---

### Notes / Troubleshooting

* If port **8000** is in use, start the backend on another port:

  ```bash
  uvicorn backend_api.main:app --reload --port 8001
  ```
* If `npm run dev` fails, ensure Node ≥ 18 and delete/reinstall `node_modules`:

  ```bash
  rm -rf node_modules package-lock.json && npm install
  ```
* If imports fail in Python, confirm the venv is activated.


