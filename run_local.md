# Running Aria AI-WebScraper Locally

With the new architecture, the Next.js frontend is deployed to a serverless platform (Vercel) whereas the FastAPI Python backend runs locally on your machine to bypass container restrictions.

To connect your local backend to the production frontend, follow these two simple steps:

### A) Start the FastAPI Backend
Open your terminal inside the project directory and start the Uvicorn server.
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```
*Your backend is now running securely on your machine.*

### B) Expose the Backend via Ngrok
In a separate terminal tab, use Ngrok to create a secure tunnel. This allows the Next.js application to reach your local backend.
```bash
ngrok http 8000
```

### C) Configure Next.js (Optional / Vercel only)
Once ngrok starts, it will give you a public URL (e.g. `https://<random-id>.ngrok-free.app`). 
Set this as the `NEXT_PUBLIC_API_URL` environment variable in Vercel. 
(For purely local testing, you don't need ngrok if your frontend connects to `http://localhost:8000`).
