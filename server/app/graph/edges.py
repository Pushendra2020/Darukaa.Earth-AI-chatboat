from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    load_conversation,
    understand_query,
    check_required_context,
    clarification,
    build_context,
    hybrid_retrieval,
    evidence_aggregation,
    multi_metric_reasoning,
    recommendation_generation,
    evidence_validation,
    refine_response,
    format_response
)

def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("load_conversation", load_conversation)
    workflow.add_node("understand_query", understand_query)
    workflow.add_node("check_required_context", check_required_context)
    workflow.add_node("clarification", clarification)
    workflow.add_node("build_context", build_context)
    workflow.add_node("hybrid_retrieval", hybrid_retrieval)
    workflow.add_node("evidence_aggregation", evidence_aggregation)
    workflow.add_node("multi_metric_reasoning", multi_metric_reasoning)
    workflow.add_node("recommendation_generation", recommendation_generation)
    workflow.add_node("evidence_validation", evidence_validation)
    workflow.add_node("refine_response", refine_response)
    workflow.add_node("format_response", format_response)
    
    workflow.set_entry_point("load_conversation")
    workflow.add_edge("load_conversation", "understand_query")
    workflow.add_edge("understand_query", "check_required_context")
    
    def route_context(state: GraphState):
        if state.get("clarification_required"):
            return "clarification"
        return "build_context"
        
    workflow.add_conditional_edges("check_required_context", route_context)
    workflow.add_edge("clarification", END)
    
    workflow.add_edge("build_context", "hybrid_retrieval")
    workflow.add_edge("hybrid_retrieval", "evidence_aggregation")
    
    def route_evidence(state: GraphState):
        if state.get("final_response"):
            return END
        return "multi_metric_reasoning"
        
    workflow.add_conditional_edges("evidence_aggregation", route_evidence)
    
    workflow.add_edge("multi_metric_reasoning", "recommendation_generation")
    workflow.add_edge("recommendation_generation", "evidence_validation")
    
    def route_validation(state: GraphState):
        results = state.get("validation_results", [])
        all_valid = all(r.get("supported", False) for r in results)
        count = state.get("refinement_count", 0)
        
        if all_valid or count >= 2:
            return "format_response"
        return "refine_response"
        
    workflow.add_conditional_edges("evidence_validation", route_validation)
    workflow.add_edge("refine_response", "evidence_validation")
    workflow.add_edge("format_response", END)
    
    return workflow.compile()

graph = build_graph()
