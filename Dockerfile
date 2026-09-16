# Multi-stage / Lightweight Production Dockerfile for FruitFresh AI
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5005 \
    TF_ENABLE_ONEDNN_OPTS=0

WORKDIR /app

# Install essential system dependencies for Pillow and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY . .

# Expose port
EXPOSE 5005

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start production server using Gunicorn WSGI
CMD exec gunicorn web_app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:${PORT}
