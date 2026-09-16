# Production Dockerfile optimized for Hugging Face Spaces & Cloud Containers
FROM python:3.11-slim

# Hugging Face Spaces listens on port 7860 by default
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    TF_ENABLE_ONEDNN_OPTS=0

# Install essential system dependencies for OpenCV/Pillow and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user with UID 1000 (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user
WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and models with proper user permissions
COPY --chown=user:user . /app

# Switch to non-root user
USER user

# Expose port 7860 for Hugging Face Spaces
EXPOSE 7860

# Start production server using Gunicorn WSGI
CMD exec gunicorn web_app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:${PORT:-7860}
