# 🚀 Nexus Scraper - Run Guide

This guide details how to run the application using either the **Streamlit UI** (Standalone) or the **React UI** (Client-Server).

## ✅ Prerequisites

Ensure you have the following installed:
1. **Python 3.8+**
2. **Node.js 18+** (for React UI only)
3. **Google Chrome** (for Selenium scraping)

---

## 🔹 Option 1: Run Streamlit UI (Standalone)

The Streamlit version runs as a single python application.

### 1. Set up Python Environment
Open your terminal in the project root `C:\Users\admin\PycharmProjects\PythonProject1`.

```powershell
# Activate Virtual Environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt
```

### 2. Run the App
```powershell
streamlit run app.py
```

*   The app will open automatically in your browser at `http://localhost:8501`.
*   This runs the UI and logic together in one process.

---

## 🔹 Option 2: Run React UI (Modern Dashboard)

The React version requires running two separate terminals: one for the **Python Backend API** and one for the **Next.js Frontend**.

### Terminal 1: Python API Server

OPEN A NEW TERMINAL in the project root.

```powershell
# 1. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 2. Install Dependencies (if not done)
pip install -r requirements.txt

# 3. Start the API Server
python api_server.py
```

*   You should see: `[INFO] API URL: http://localhost:8000`
*   Keep this terminal open.

### Terminal 2: Next.js Frontend

OPEN A SEPARATE TERMINAL.

```powershell
# 1. Navigate to the UI directory
cd nexus-scraper-ui

# 2. Install Node Dependencies (First time only)
npm install

# 3. Start the Development Server
npm run dev
```

*   You will see: `Ready in [...] http://localhost:3000`
*   Open **http://localhost:3000** in your browser.

---

## 🛠 Troubleshooting

*   **Port Config**:
    *   Backend runs on **Port 8000**.
    *   Frontend runs on **Port 3000**.
    *   Streamlit runs on **Port 8501**.
*   **Database**: The app uses local artifacts/files; no database setup is required for this version.
*   **API Keys**: Ensure your `.env` file (if used) or environment variables are set up for Gemini API if `ai_agent.py` requires it.
