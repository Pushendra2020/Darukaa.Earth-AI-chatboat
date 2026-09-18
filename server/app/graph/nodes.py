import json
from app.graph.state import GraphState
from app.core.llm import generate_structured, generate_text, get_embeddings
from app.db.supabase import get_conversation, save_message, vector_search, structured_search, get_metric_relationships
from app.core.config import settings

def load_conversation(state: GraphState) -> GraphState:
    conv_id = state.get("conversation_id")
    if conv_id:
        messages = get_conversation(conv_id)
        state["messages"] = messages
    else:
        state["messages"] = []
    return state

def understand_query(state: GraphState) -> GraphState:
    query = state.get("user_query", "")
    schema = {
        "title": "Intent",
        "type": "object",
        "properties": {
            "goal": {"type": "string"},
            "metrics": {"type": "array", "items": {"type": "string"}},
            "ecosystem": {"type": "string"},
            "land_use": {"type": "string"},
            "location": {"type": "string"}
        }
    }
    prompt = f"Analyze the following user query and extract the environmental intent:\n\nQuery: {query}"
    intent = generate_structured(prompt, schema)
    state["intent"] = intent
    return state

def check_required_context(state: GraphState) -> GraphState:
    intent = state.get("intent", {})
    context = state.get("environmental_context", {})
    missing_metrics = []
    
    if not context.get("land", {}).get("land_use") and not intent.get("land_use"):
        missing_metrics.append("land_use")
    if not context.get("climate", {}).get("rainfall"):
        missing_metrics.append("rainfall")
        
    if missing_metrics:
        state["clarification_required"] = True
        state["missing_metrics"] = missing_metrics
    else:
        state["clarification_required"] = False
        state["missing_metrics"] = []
        
    return state

def clarification(state: GraphState) -> GraphState:
    missing = state.get("missing_metrics", [])
    prompt = f"Ask a concise, conversational question to the user asking for the following missing environmental information: {', '.join(missing)}"
    question = generate_text(prompt)
    
    state["final_response"] = {
        "conversation_id": state.get("conversation_id"),
        "answer": question,
        "clarification_required": True,
        "recommendations": []
    }
    
    # Save conversation state
    if state.get("conversation_id"):
        save_message(state["conversation_id"], {"role": "assistant", "content": question})
        
    return state

def build_context(state: GraphState) -> GraphState:
    # Ensure context is formatted correctly
    # Just passing through user provided context for now
    return state

def hybrid_retrieval(state: GraphState) -> GraphState:
    query = state.get("user_query", "")
    intent = state.get("intent", {})
    context = state.get("environmental_context", {})
    
    # Vector Search
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)
    v_results = vector_search(query_vector, settings.VECTOR_TOP_K)
    state["retrieved_chunks"] = v_results
    
    # Structured Search
    s_results = structured_search(intent, settings.STRUCTURED_TOP_K)
    state["structured_matches"] = s_results
    
    # Relationships
    metrics = intent.get("metrics", [])
    if metrics:
        rels = get_metric_relationships(metrics)
        state["metric_relationships"] = rels
        
    return state

def evidence_aggregation(state: GraphState) -> GraphState:
    v_chunks = state.get("retrieved_chunks", [])
    s_chunks = state.get("structured_matches", [])
    
    # Simple deduplication
    evidence_map = {}
    for chunk in v_chunks + s_chunks:
        # Depending on how rpc and table returns data, handle id
        chunk_id = chunk.get("id") or chunk.get("chunk_id")
        if chunk_id and chunk_id not in evidence_map:
            evidence_map[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": chunk.get("document_id"),
                "content": chunk.get("content", ""),
                "title": chunk.get("documents", {}).get("title", "") if isinstance(chunk.get("documents"), dict) else chunk.get("title", ""),
                "year": chunk.get("documents", {}).get("publication_year", "") if isinstance(chunk.get("documents"), dict) else chunk.get("publication_year", ""),
                "page": chunk.get("page_start", "")
            }
            
    evidence = list(evidence_map.values())[:settings.FINAL_EVIDENCE_COUNT]
    state["evidence"] = evidence
    
    # If no evidence, handle gracefully
    if not evidence:
        state["final_response"] = {
            "conversation_id": state.get("conversation_id"),
            "answer": "I don't have enough evidence in the current knowledge base to make a reliable recommendation.",
            "clarification_required": True,
            "recommendations": []
        }
        
    return state

def multi_metric_reasoning(state: GraphState) -> GraphState:
    # Skip if final_response is already set (e.g. no evidence)
    if state.get("final_response"): return state
    
    evidence = state.get("evidence", [])
    rels = state.get("metric_relationships", [])
    context = state.get("environmental_context", {})
    
    prompt = f"Reason across these metrics given the context: {context}\nEvidence: {evidence}\nRelationships: {rels}\nProvide causal pathways and tradeoffs."
    reasoning = generate_text(prompt)
    state["reasoning"] = {"summary": reasoning}
    return state

def recommendation_generation(state: GraphState) -> GraphState:
    if state.get("final_response"): return state
    
    reasoning = state.get("reasoning", {})
    evidence = state.get("evidence", [])
    
    schema = {
        "title": "Recommendations",
        "type": "object",
        "properties": {
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "why_it_works": {"type": "string"},
                        "impacted_metrics": {"type": "array", "items": {"type": "string"}},
                        "time_horizon": {"type": "string"},
                        "conditions": {"type": "array", "items": {"type": "string"}},
                        "evidence_ids": {"type": "array", "items": {"type": "string"}},
                        "confidence": {"type": "number"}
                    }
                }
            }
        }
    }
    
    prompt = f"Based on reasoning: {reasoning} and evidence: {evidence}, generate specific recommendations. Do NOT invent numerical effects."
    recs_obj = generate_structured(prompt, schema)
    state["recommendations"] = recs_obj.get("recommendations", []) if recs_obj else []
    return state

def evidence_validation(state: GraphState) -> GraphState:
    if state.get("final_response"): return state
    
    recs = state.get("recommendations", [])
    # In a real app we'd ask the LLM to validate against the evidence set.
    # For MVP we pass them as valid.
    state["validation_results"] = [{"supported": True} for _ in recs]
    return state

def refine_response(state: GraphState) -> GraphState:
    count = state.get("refinement_count", 0)
    state["refinement_count"] = count + 1
    # refinement logic goes here
    return state

def format_response(state: GraphState) -> GraphState:
    if state.get("final_response"): return state
    
    recs = state.get("recommendations", [])
    evidence = state.get("evidence", [])
    
    # Map evidence IDs to full evidence objects for the UI
    for rec in recs:
        rec_evs = []
        for eid in rec.get("evidence_ids", []):
            for e in evidence:
                if e["chunk_id"] == eid:
                    rec_evs.append(e)
        rec["evidence"] = rec_evs
    
    answer = "Based on the evidence retrieved from the knowledge base, here are the recommendations."
    
    state["final_response"] = {
        "conversation_id": state.get("conversation_id"),
        "answer": answer,
        "clarification_required": False,
        "recommendations": recs
    }
    
    if state.get("conversation_id"):
        save_message(state["conversation_id"], {"role": "assistant", "content": answer})
        
    return state
