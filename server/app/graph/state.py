from typing import TypedDict

class GraphState(TypedDict, total=False):
    conversation_id: str
    user_id: str | None

    messages: list
    user_query: str

    intent: dict

    required_metrics: list[str]
    missing_metrics: list[str]
    clarification_required: bool

    environmental_context: dict

    retrieved_chunks: list[dict]
    structured_matches: list[dict]
    metric_relationships: list[dict]

    evidence: list[dict]

    reasoning: dict

    recommendations: list[dict]

    validation_results: list[dict]

    refinement_count: int

    final_response: dict
