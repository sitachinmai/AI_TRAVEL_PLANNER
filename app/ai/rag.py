from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.ai.tools import tool_search_destinations, tool_get_destination_details


class TravelRAGRetriever:
    """
    Retrieval-Augmented Generation (RAG) retriever fetching authoritative local SQLite travel context.
    """

    @classmethod
    def retrieve_context(cls, db: Session, query: str) -> Dict[str, Any]:
        destinations = tool_search_destinations(db, query)
        if not destinations:
            return {"query": query, "context_found": False, "destinations": []}

        detailed = tool_get_destination_details(db, destinations[0]["id"])
        return {
            "query": query,
            "context_found": True,
            "destination": detailed
        }
