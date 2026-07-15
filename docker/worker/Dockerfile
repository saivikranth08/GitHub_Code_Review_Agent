FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck probing
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install base Python dependencies (shared with api)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install CPU-only PyTorch + sentence-transformers (worker exclusive)
# CPU-only = ~200MB instead of 900MB with CUDA — we don't need GPU for embeddings
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir sentence-transformers>=3.1.0

# Pre-download the embedding model at BUILD time (zero cold-start)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy app code and prompts
COPY app/ ./app/
COPY prompts/ ./prompts/

# CMD is set per-service in docker-compose.yml
