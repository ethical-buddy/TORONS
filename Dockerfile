FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libev-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    tor \
 && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add app code
COPY . /app
WORKDIR /app

# Default run command
CMD tor & python3 main.py
