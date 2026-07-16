FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck probing
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install base Python dependencies (shared with api)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy app code and prompts
COPY app/ ./app/
COPY prompts/ ./prompts/

# CMD is set per-service in docker-compose.yml
