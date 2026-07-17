import uuid
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from app.config import settings
from app.models.finding import Finding
import structlog

logger = structlog.get_logger()

class QdrantStore:
    """
    Manages long-term memory for the AI agents using Qdrant vector database.
    Code patterns and bugs are converted to embeddings via Cohere and stored here.
    """
    
    def __init__(self):
        # 1. Connect to Qdrant (our local Docker container)
        self.qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        
        # 2. Connect to Cohere (for creating mathematical vectors from text)
        self.cohere = cohere.Client(settings.cohere_api_key)
        self.collection = settings.qdrant_collection

    def _get_embedding(self, text: str, input_type: str = "search_document") -> list[float]:
        """
        Converts text into a vector using Cohere's embed-english-v3.0 model.
        """
        try:
            response = self.cohere.embed(
                texts=[text],
                model=settings.embedding_model,
                input_type=input_type
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error("cohere_embedding_failed", error=str(e))
            return []

    def save_finding(self, pr_number: int, repo: str, finding: Finding):
        """
        Saves an AI finding into Qdrant so agents can remember it for future PRs.
        """
        # We want the vector to mathematically represent the bug description and the suggestion
        text_to_embed = f"Issue: {finding.title}\n{finding.description}\nFix: {finding.suggestion}"
        
        vector = self._get_embedding(text_to_embed, input_type="search_document")
        if not vector:
            return
            
        point_id = str(uuid.uuid4())
        
        self.qdrant.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "pr_number": pr_number,
                        "repo": repo,
                        "file_path": finding.file_path,
                        "severity": finding.severity,
                        "category": finding.category,
                        "title": finding.title,
                        "description": finding.description,
                        "suggestion": finding.suggestion
                    }
                )
            ]
        )
        logger.info("finding_saved_to_qdrant", id=point_id, category=finding.category)

    def search_similar_code(self, current_diff: str, limit: int = 2) -> str:
        """
        Searches Qdrant for past bugs that look mathematically similar to the current code diff.
        Returns a formatted string of past bugs to inject into the Groq prompt.
        """
        vector = self._get_embedding(current_diff, input_type="search_query")
        if not vector:
            return ""
            
        try:
            search_result = self.qdrant.search(
                collection_name=self.collection,
                query_vector=vector,
                limit=limit,
                score_threshold=0.35  # Only return somewhat relevant matches
            )
            
            if not search_result:
                return ""
                
            past_context = "### PAST SIMILAR BUGS FOUND IN THIS REPOSITORY:\n"
            past_context += "Use these past bugs as context. If the current code contains these EXACT SAME mistakes, flag them heavily.\n\n"
            
            for hit in search_result:
                payload = hit.payload
                past_context += f"- Past Issue: {payload['title']} ({payload['severity']})\n"
                past_context += f"  Explanation: {payload['description']}\n"
                past_context += f"  How we fixed it before:\n  {payload['suggestion']}\n\n"
                
            logger.info("found_similar_past_bugs", count=len(search_result))
            return past_context
            
        except Exception as e:
            logger.error("qdrant_search_failed", error=str(e))
            return ""
