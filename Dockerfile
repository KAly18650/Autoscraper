FROM python:3.12-slim

# Install OS deps as needed (e.g. for Playwright, if you want to run it inside container)
# Include required libraries for Chromium/Playwright using valid Debian package names
RUN apt-get update && apt-get install -y \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libexpat1 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
# The --with-deps flag installs ALL required system libraries automatically
RUN playwright install --with-deps chromium

# Copy the rest of your project
COPY . .

# Expose ADK web port (default is 8000)
EXPOSE 8000

# Environment variables will be provided at deploy time:
# - GEMINI_API_KEY_FILE
# - GCS_BUCKET_NAME
# - GCP_PROJECT_ID
# - GOOGLE_APPLICATION_CREDENTIALS (pointing to mounted JSON in the container)

# Start ADK Web pointing at the orchestrator package
# Bind to 0.0.0.0 so Cloud Run can access the health check endpoint
CMD ["adk", "web", "--host", "0.0.0.0"]