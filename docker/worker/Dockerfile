FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck probing
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Sentence Transformer embedding model at BUILD time
# This bakes the model into the image — zero cold-start delay when worker starts
# Model: all-MiniLM-L6-v2 (384 dimensions, 80MB, runs on CPU, completely free)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy app code and prompts
COPY app/ ./app/
COPY prompts/ ./prompts/

# CMD is NOT set here — it's defined per-service in docker-compose.yml
# worker:      celery -A app.workers.celery_app worker --loglevel=info --concurrency=4 -Q reviews
# worker-beat: celery -A app.workers.celery_app beat --loglevel=info
