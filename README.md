# Quick Links
-  [ai_base](https://github.com/lucib3196/GestatlQuestions/tree/main/backend/src/ai_base) (in Progress) : A set of basic LLM features including multimodal inputs of image and pdf with code snippets. 

# Gestalt Question Review — Local Setup

## Prerequisites

Before you begin, make sure you have the following installed:

* **Git**
* **Python ≥ 3.10**
* **Node.js ≥ 18** (with npm)
* **Poetry ≥ 1.8** → [Installation Guide](https://python-poetry.org/docs/#installation)

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/lucib3196/Gestalt_Question_Review.git
cd Gestalt_Question_Review
```

---

## 2️⃣ Environment Variables

Create a `.env` file in the project root with the required API keys and configuration settings.
For a default env file email me at lberm007@ucr.edu

Example:

```env
# Example .env file
OPENAI_API_KEY=your_openai_api_key_here
FIREBASE_API_KEY=your_firebase_key_here
DATABASE_URL=sqlite:///./app.db
```

---

## 3️⃣ Install Backend Dependencies with Poetry

Poetry will automatically create and manage a virtual environment for the project.

Go into backend directory and install dependencies 
```bash
cd backend
poetry install
```


---

## 4️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## 5️⃣ Run the Backend (FastAPI)

Start the FastAPI backend:

```bash
cd backend // Ensure you're in the backend folder
poetry run python -m  src.api.main
```

**Endpoints:**

* API Root → [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Swagger Docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 6️⃣ Run the Frontend (Vite)

In a separate terminal:

```bash
cd frontend
npm run dev
```

Your local development server will start — usually at:
👉 [http://localhost:5173](http://localhost:5173)

---


## 🧠 Need Help?

If you run into issues or setup problems, feel free to reach out:
📧 **[lberm007@ucr.edu](mailto:lberm007@ucr.edu)**

---
