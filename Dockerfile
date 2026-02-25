FROM python:3.11-slim

# Install Chromium and dependencies for DrissionPage
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2t64 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Chromium path for DrissionPage
ENV CHROMIUM_PATH=/usr/bin/chromium
ENV RENDER=true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python source files
COPY *.py .

EXPOSE 8000

# Use shell form to expand the $PORT environment variable injected by Render
# If $PORT is not set (e.g., running locally), default back to 8000
CMD uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8000}
