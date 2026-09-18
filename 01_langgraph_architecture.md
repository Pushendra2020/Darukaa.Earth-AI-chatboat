# Darukaa.Earth Biodiversity Intelligence

## LangGraph Architecture

### 1. Purpose

The backend is a Python FastAPI application with LangGraph orchestrating
a stateful, multi-step environmental reasoning workflow.

The graph should not be a generic chatbot chain. Its job is to:

1.  Understand the user's environmental question.
2.  Detect missing information and ask clarifying questions when
    necessary.
3.  Maintain conversation state.
4.  Build a structured environmental context.
5.  Perform hybrid retrieval from the existing biodiversity knowledge
    base.
6.  Reason across multiple environmental metrics.
7.  Generate evidence-backed recommendations.
8.  Validate every recommendation against retrieved evidence.
9.  Return a structured answer to the Next.js frontend.

------------------------------------------------------------------------

## 2. High-Level Graph

``` text
START
  |
  v
[load_conversation]
  |
  v
[understand_query]
  |
  v
[check_required_context]
  |
  +--------------------+
  |                    |
  | missing context    | sufficient context
  v                    v
[clarification]   [build_context]
  |                    |
  v                    v
END                 [hybrid_retrieval]
                         |
                         v
                  [evidence_aggregation]
                         |
                         v
                  [multi_metric_reasoning]
                         |
                         v
                  [recommendation_generation]
                         |
                         v
                  [evidence_validation]
                         |
                  +------+------+
                  |             |
              valid            invalid
                  |             |
                  v             v
            [format_response] [refine_response]
                  |             |
                  |             +----> [evidence_validation]
                  v
                 END
```

------------------------------------------------------------------------

## 3. LangGraph State

Use one typed state object shared by every node.

Recommended fields:

``` python
class GraphState(TypedDict, total=False):
    conversation_id: str
    user_id: str | None

    messages: list

    user_query: str

    intent: dict

    required_metrics: list[str]
    missing_metrics: list[str]

    environmental_context: dict

    retrieved_chunks: list[dict]
    structured_matches: list[dict]

    evidence: list[dict]

    metric_relationships: list[dict]

    reasoning: dict

    recommendations: list[dict]

    validation_results: list[dict]

    final_response: dict

    clarification_required: bool
```

Keep the state explicit. Do not hide important reasoning data inside
arbitrary strings.

------------------------------------------------------------------------

# 4. Nodes

## Node 1: `load_conversation`

### Responsibility

Load previous conversation context using `conversation_id`.

### Input

-   `conversation_id`
-   current user message

### Output

-   previous messages
-   relevant conversation memory

### Behavior

The node should retrieve only the context necessary for the current
conversation.

Do not send an unlimited conversation history to the LLM.

------------------------------------------------------------------------

## Node 2: `understand_query`

### Responsibility

Convert natural language into structured environmental intent.

Example:

``` text
"My farm has declining biodiversity and dry soil."
```

Possible structured output:

``` json
{
  "intent": "biodiversity_decline",
  "metrics": [
    "species_richness",
    "soil_moisture"
  ],
  "ecosystem": "agricultural_land",
  "requested_action": true
}
```

The node should identify:

-   environmental objective
-   mentioned metrics
-   ecosystem/land type
-   intervention context
-   geographic information
-   time information
-   uncertainty
-   missing information

The LLM should output structured JSON.

------------------------------------------------------------------------

## Node 3: `check_required_context`

### Responsibility

Determine whether enough information exists to perform meaningful
multi-metric reasoning.

Example:

``` text
User:
"Biodiversity is declining."
```

The system should not immediately invent an intervention.

It may identify:

``` text
Required context:
- land use
- rainfall / water availability
- soil organic carbon or soil condition
```

If important information is missing:

``` text
clarification_required = true
missing_metrics = [...]
```

Then route to `clarification`.

------------------------------------------------------------------------

## Node 4: `clarification`

### Responsibility

Ask a concise, useful clarification question.

Example:

``` text
To narrow this down, what is the approximate annual rainfall,
land use, and soil organic carbon level of the area?
```

The question should prioritize variables that materially change the
recommendation.

The node should not ask for every possible environmental variable.

If enough information becomes available in the conversation, the next
turn can continue through the graph.

------------------------------------------------------------------------

## Node 5: `build_context`

### Responsibility

Create a normalized environmental context.

Example:

``` json
{
  "location": {
    "latitude": 19.03,
    "longitude": 73.02,
    "district": "..."
  },
  "soil": {
    "organic_carbon": 0.42,
    "ph": 6.8,
    "moisture": 18
  },
  "climate": {
    "rainfall": 820,
    "temperature": 27
  },
  "land": {
    "land_use": "cropland"
  },
  "biodiversity": {
    "species_richness": null
  }
}
```

Separate:

-   user-provided values
-   external environmental data
-   inferred values

Never represent an inferred value as an observed measurement.

------------------------------------------------------------------------

# 5. Node 6: `hybrid_retrieval`

### Responsibility

Retrieve scientific evidence using two complementary mechanisms:

1.  Vector similarity
2.  Structured filtering

Vector retrieval finds semantically relevant scientific text.

Structured retrieval finds evidence matching explicit constraints such
as:

-   environmental variable
-   intervention
-   ecosystem
-   geography
-   climate zone
-   evidence type
-   publication year

The retrieval process is described in detail in
`03_hybrid_retrieval.md`.

------------------------------------------------------------------------

# 6. Node 7: `evidence_aggregation`

### Responsibility

Turn raw retrieval results into a compact evidence set.

For every candidate evidence item keep:

``` json
{
  "chunk_id": "...",
  "document_id": "...",
  "claim": "...",
  "source": "...",
  "page_start": 10,
  "page_end": 12,
  "metric": "soil_organic_carbon",
  "direction": "positive",
  "effect_size": null,
  "conditions": ["agroforestry"],
  "relevance_score": 0.87
}
```

Deduplicate evidence from the same document where appropriate.

Prefer evidence that directly supports the intended intervention and
environmental conditions.

------------------------------------------------------------------------

# 7. Node 8: `multi_metric_reasoning`

### Responsibility

This is the core intelligence layer.

The node should reason across at least three related environmental
variables whenever the query allows it.

Example:

``` text
Rainfall
   |
   v
Soil moisture
   |
   v
Vegetation condition
   |
   v
Habitat quality
   |
   v
Species richness
```

Another relationship:

``` text
Land-use intensification
        |
        v
Habitat fragmentation
        |
        v
Reduced habitat connectivity
        |
        v
Biodiversity decline
```

The reasoning node should:

1.  Read the environmental context.
2.  Read retrieved evidence.
3.  Read metric relationships.
4.  Identify causal/associational pathways supported by evidence.
5.  Identify trade-offs.
6.  Determine which intervention is applicable under the current
    conditions.
7.  Produce a reasoning trace that can be summarized for the user.

Do not let the LLM invent causal relationships that are absent from the
knowledge layer.

------------------------------------------------------------------------

# 8. Node 9: `recommendation_generation`

Each recommendation must have a fixed schema.

``` json
{
  "action": "...",
  "why_it_works": "...",
  "impacted_metrics": [
    "soil_organic_carbon",
    "soil_moisture",
    "habitat_diversity"
  ],
  "time_horizon": "...",
  "conditions": ["..."],
  "evidence_ids": ["..."],
  "confidence": 0.0
}
```

The recommendation must answer:

-   What should be done?
-   Why should it work?
-   Which metrics should change?
-   Under what conditions?
-   Over what time horizon?
-   What evidence supports it?

Avoid generic recommendations such as:

``` text
"Use sustainable agricultural practices."
```

Instead produce a specific, conditional intervention grounded in
retrieved evidence.

------------------------------------------------------------------------

# 9. Node 10: `evidence_validation`

This node is mandatory.

For every generated recommendation:

``` text
Recommendation
      |
      v
Evidence validator
      |
      +---- supported ----> keep
      |
      +---- partially supported -> qualify
      |
      +---- unsupported ----> remove
```

Validation should check:

-   Does the cited evidence actually support the action?
-   Does it support the claimed metric impact?
-   Does it support the direction of change?
-   Does it support any numerical effect size?
-   Are the environmental conditions compatible?
-   Is the source actually present in the retrieved knowledge base?

Numerical claims must be directly supported by retrieved evidence.

If evidence says:

``` text
"Agroforestry can increase soil organic carbon."
```

the model must not produce:

``` text
"Agroforestry increases soil organic carbon by 25%."
```

unless the retrieved source explicitly supports that number.

------------------------------------------------------------------------

# 10. Node 11: `refine_response`

If validation finds unsupported or overconfident claims:

1.  Remove unsupported claims.
2.  Qualify uncertain claims.
3.  Re-generate only the affected recommendation.
4.  Re-run validation.

Limit the number of refinement loops to prevent infinite graph
execution.

Recommended:

``` python
MAX_REFINEMENT_LOOPS = 2
```

------------------------------------------------------------------------

# 11. Node 12: `format_response`

Return a stable API response to the frontend.

Recommended response:

``` json
{
  "conversation_id": "...",
  "answer": "...",
  "recommendations": [
    {
      "action": "...",
      "why_it_works": "...",
      "impacted_metrics": [],
      "time_horizon": "...",
      "confidence": 0.82,
      "evidence": [
        {
          "title": "...",
          "year": 2022,
          "page": 15
        }
      ]
    }
  ],
  "clarification_required": false
}
```

------------------------------------------------------------------------

# 12. Conditional Edges

Recommended routing:

``` python
START
 -> load_conversation
 -> understand_query
 -> check_required_context

check_required_context:
    missing -> clarification -> END
    sufficient -> build_context

build_context
 -> hybrid_retrieval
 -> evidence_aggregation
 -> multi_metric_reasoning
 -> recommendation_generation
 -> evidence_validation

evidence_validation:
    valid -> format_response -> END
    invalid -> refine_response -> evidence_validation
```

------------------------------------------------------------------------

# 13. FastAPI Integration

FastAPI should be the transport/API layer.

Do not put retrieval or reasoning logic directly inside FastAPI routes.

Recommended structure:

``` text
FastAPI Route
     |
     v
Graph Service
     |
     v
LangGraph
     |
     +--> Conversation Memory
     +--> Hybrid Retrieval
     +--> Metric Relationships
     +--> Evidence Validation
     |
     v
Structured Response
     |
     v
FastAPI
     |
     v
Next.js
```

Suggested endpoint:

``` http
POST /api/chat
```

Request:

``` json
{
  "conversation_id": "uuid",
  "message": "Biodiversity is declining on my farm",
  "environment": {
    "rainfall": 800,
    "soil_organic_carbon": 0.4,
    "land_use": "cropland"
  },
  "location": {
    "latitude": 19.03,
    "longitude": 73.02
  }
}
```

The endpoint should stream or return the graph's final structured
result.

------------------------------------------------------------------------

# 14. LangGraph Design Principles

### Keep nodes single-purpose

Bad:

``` text
one giant agent does everything
```

Good:

``` text
query understanding
context validation
retrieval
reasoning
recommendation
validation
```

### Keep retrieval deterministic

Retrieval should not depend entirely on an LLM deciding what database
query to run.

### Keep scientific evidence separate from conversation memory

Conversation memory describes the user's situation.

The knowledge base describes scientific evidence.

Do not mix them.

### Treat the evidence validator as a safety boundary

The generator proposes.

The validator decides whether the proposal is supported by retrieved
evidence.

### Make the graph observable

Log:

-   node name
-   execution time
-   retrieval count
-   selected evidence
-   validation result
-   final recommendation IDs

Do not log API keys or sensitive user information.
