# Initialize Qdrant vector store collection on first startup
# Run with: docker compose exec api python scripts/init_qdrant.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff
from app.config import settings


def init_qdrant():
    print("🔌 Connecting to Qdrant...")
    client = QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )

    existing = [c.name for c in client.get_collections().collections]

    if settings.qdrant_collection not in existing:
        print(f"📦 Creating collection: '{settings.qdrant_collection}'")
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=1024,              # cohere embed-english-v3.0 output dimensions
                distance=Distance.COSINE  # cosine similarity for semantic search
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=1000  # build index after 1000 vectors
            ),
        )
        print(f"✅ Qdrant collection '{settings.qdrant_collection}' created")
        print(f"   Vector size: 1024 (Cohere embed-english-v3.0)")
        print(f"   Distance: Cosine similarity")
    else:
        print(f"✅ Qdrant collection '{settings.qdrant_collection}' already exists — skipping")


if __name__ == "__main__":
    init_qdrant()
