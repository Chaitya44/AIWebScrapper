FROM python:3.11-slim

# Install Chromium and dependencies for DrissionPage
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Set Chromium path for DrissionPage
ENV CHROMIUM_PATH=/usr/bin/chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python source files
COPY api_server.py .
COPY scraper.py .
COPY gemini_organizer.py .
COPY ai_agent.py .
COPY captcha_handler.py .
COPY auth.py .

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
