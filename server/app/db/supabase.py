import json
from supabase import create_client, Client
from app.core.config import settings

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def get_conversation(conversation_id: str) -> list[dict]:
    # Placeholder for a potential messages table
    # If not present, we can just return empty list and handle it in the node.
    try:
        response = supabase.table("conversations").select("messages").eq("id", conversation_id).execute()
        if response.data:
            return response.data[0].get("messages", [])
    except Exception as e:
        pass
    return []

def save_message(conversation_id: str, message: dict):
    # This requires the conversations table to exist.
    # We will upsert the conversation
    try:
        messages = get_conversation(conversation_id)
        messages.append(message)
        supabase.table("conversations").upsert({"id": conversation_id, "messages": messages}).execute()
    except Exception as e:
        pass

def vector_search(query_embedding: list[float], top_k: int = 20) -> list[dict]:
    try:
        response = supabase.rpc("match_document_chunks", {
            "query_embedding": query_embedding,
            "match_count": top_k
        }).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error in vector search: {e}")
        return []

def structured_search(filters: dict, top_k: int = 20) -> list[dict]:
    # Very basic structured search logic matching topics/variables/interventions
    # against document_chunks
    try:
        query = supabase.table("document_chunks").select("*, documents(*)")
        # Just an example of applying filters
        if "metrics" in filters and filters["metrics"]:
            query = query.contains("variables", filters["metrics"])
        if "ecosystem" in filters and filters["ecosystem"]:
            query = query.contains("topics", [filters["ecosystem"]])
            
        response = query.limit(top_k).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error in structured search: {e}")
        return []

def get_metric_relationships(metrics: list[str]) -> list[dict]:
    try:
        response = supabase.table("metric_relationships").select("*").in_("source_metric", metrics).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error in get_metric_relationships: {e}")
        return []
