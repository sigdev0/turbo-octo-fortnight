FROM python:3.11-slim

# Install system dependencies (ffmpeg is required for audio mixing and video processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Ensure storage directories exist
RUN mkdir -p /app/output /app/data /app/assets/music /app/backlog

# Run OmniForge bot in daemon mode
CMD ["python", "main.py", "--run"]
