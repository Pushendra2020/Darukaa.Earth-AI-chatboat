# Coding Agent Prompt

## Darukaa.Earth Biodiversity Intelligence System

You are implementing the production MVP of the Darukaa.Earth
Biodiversity Intelligence challenge.

The knowledge base ingestion layer is already completed. Do NOT rebuild
the ingestion pipeline.

Your task is to build the application layer on top of the existing
knowledge base.

------------------------------------------------------------------------

# 1. Existing Technology

## Frontend

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS

## Backend

-   Python
-   FastAPI
-   LangGraph
-   Pydantic

## Knowledge Base

-   Supabase
-   PostgreSQL
-   pgvector
-   Existing tables:
    -   `documents`
    -   `document_chunks`
    -   `research_observations`
    -   `metric_relationships`

## Embeddings

The existing knowledge base uses:

``` text
nvidia/llama-nemotron-embed-vl-1b-v2:free
```

through OpenRouter.

Use the SAME embedding model for query embeddings.

Embedding dimension:

``` text
2048
```

## LLM

The application must support provider switching.

Supported providers:

``` text
openrouter
nvidia
google
```

The provider is selected through:

``` env
LLM_PROVIDER=openrouter
```

Do not hard-code the provider inside LangGraph nodes.

------------------------------------------------------------------------

# 2. Primary Objective

Build an AI environmental scientist, not a generic chatbot.

The system must:

1.  Understand environmental questions.
2.  Maintain conversational context.
3.  Ask clarifying questions when important environmental information is
    missing.
4.  Retrieve scientific evidence.
5.  Use hybrid retrieval.
6.  Reason across multiple environmental variables.
7.  Generate specific recommendations.
8.  Explain scientific reasoning.
9.  Identify impacted environmental metrics.
10. Provide a time horizon.
11. Cite supporting research/report evidence.
12. Validate generated recommendations against retrieved evidence.
13. Avoid unsupported numerical claims.

------------------------------------------------------------------------

# 3. DO NOT Rebuild

Do NOT:

-   rebuild PDF ingestion
-   download research papers
-   recreate embeddings
-   recreate the Supabase knowledge base
-   replace the existing database schema unless absolutely required
-   create a second unrelated vector database
-   move the backend to Node.js
-   implement LangGraph in TypeScript

The backend MUST use Python LangGraph.

------------------------------------------------------------------------

# 4. Backend Architecture

Create:

``` text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   └── chat.py
    │
    ├── schemas/
    │   └── chat.py
    │
    ├── graph/
    │   ├── state.py
    │   ├── graph.py
    │   └── nodes/
    │       ├── conversation.py
    │       ├── query_understanding.py
    │       ├── context.py
    │       ├── retrieval.py
    │       ├── evidence.py
    │       ├── reasoning.py
    │       ├── recommendation.py
    │       └── validation.py
    │
    ├── retrieval/
    │   ├── vector.py
    │   ├── structured.py
    │   └── hybrid.py
    │
    ├── services/
    │   ├── llm.py
    │   ├── conversation.py
    │   └── evidence_validator.py
    │
    └── db/
        ├── supabase.py
        └── queries.py
```

Adjust this structure if the existing repository already has a better
organization, but preserve separation of concerns.

------------------------------------------------------------------------

# 5. LangGraph State

Implement a typed state.

Minimum fields:

``` python
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
```

Keep important state fields explicit.

------------------------------------------------------------------------

# 6. LangGraph Nodes

Implement these nodes.

## `load_conversation`

Load relevant conversation state.

Use `conversation_id`.

Do not send unlimited chat history to the LLM.

------------------------------------------------------------------------

## `understand_query`

Convert the user's natural language into structured intent.

Example:

``` json
{
  "goal": "improve_biodiversity",
  "metrics": [
    "species_richness",
    "soil_moisture"
  ],
  "ecosystem": "cropland",
  "land_use": "cropland",
  "location": null
}
```

Use structured output.

Never invent environmental measurements.

------------------------------------------------------------------------

## `check_required_context`

Determine whether sufficient context exists for meaningful reasoning.

Example:

``` text
User:
"Biodiversity is declining."
```

Possible missing context:

``` text
land_use
rainfall
soil condition
```

If important context is missing:

``` text
clarification_required = true
```

Route to clarification.

------------------------------------------------------------------------

## `clarification`

Generate one concise question that asks for the highest-value missing
information.

Do not ask for ten variables at once.

------------------------------------------------------------------------

## `build_context`

Merge:

``` text
previous conversation
+
current message
+
explicit environment input
+
location
```

Maintain provenance.

Represent:

``` text
user_observed
external_observed
inferred
unknown
```

separately where appropriate.

Never convert inference into a measurement.

------------------------------------------------------------------------

## `hybrid_retrieval`

Call the retrieval service.

It must combine:

``` text
vector retrieval
+
structured retrieval
+
metric relationship expansion
```

Use the existing Supabase knowledge base.

Return normalized evidence.

------------------------------------------------------------------------

## `evidence_aggregation`

Deduplicate and rank evidence.

Preserve:

``` text
document_id
chunk_id
title
publication_year
page_start
page_end
source_url
claims
variables
similarity
```

Prefer diverse, directly relevant evidence.

------------------------------------------------------------------------

## `multi_metric_reasoning`

This is the core reasoning node.

It must reason across multiple variables.

Example:

``` text
rainfall
  ↓
soil moisture
  ↓
vegetation
  ↓
habitat quality
  ↓
species richness
```

Or:

``` text
land use
  ↓
habitat fragmentation
  ↓
connectivity
  ↓
species richness
```

Use `metric_relationships` as a structured constraint.

Do not allow the LLM to invent scientific relationships.

The output should identify:

``` json
{
  "drivers": [],
  "relationships": [],
  "tradeoffs": [],
  "reasoning_summary": ""
}
```

------------------------------------------------------------------------

## `recommendation_generation`

Generate recommendations using ONLY the environmental context and
retrieved evidence.

Each recommendation must contain:

``` json
{
  "action": "",
  "why_it_works": "",
  "impacted_metrics": [],
  "conditions": [],
  "time_horizon": "",
  "evidence_ids": [],
  "confidence": null
}
```

Recommendations must be specific.

Bad:

``` text
"Use sustainable practices."
```

Good:

``` text
"Introduce X under Y conditions because the retrieved
evidence indicates Z, which affects A, B, and C."
```

Do not invent effect sizes.

------------------------------------------------------------------------

## `evidence_validation`

Validate every recommendation.

For every claim ask:

``` text
Does retrieved evidence support this?
```

Check:

-   intervention
-   mechanism
-   impacted metric
-   direction
-   numerical effect
-   conditions
-   source

Return:

``` json
{
  "supported": true,
  "unsupported_claims": [],
  "qualifications": []
}
```

Unsupported claims must be removed or qualified.

------------------------------------------------------------------------

## `refine_response`

If validation fails:

1.  Remove unsupported claims.
2.  Add qualifications.
3.  Regenerate only what is necessary.
4.  Run validation again.

Maximum:

``` text
2 refinement loops
```

Never create an infinite graph loop.

------------------------------------------------------------------------

## `format_response`

Return the final API schema.

------------------------------------------------------------------------

# 7. Graph Routing

Implement:

``` text
START
  |
load_conversation
  |
understand_query
  |
check_required_context
  |
  +-- missing --> clarification --> END
  |
  +-- sufficient
          |
          v
     build_context
          |
          v
    hybrid_retrieval
          |
          v
  evidence_aggregation
          |
          v
 multi_metric_reasoning
          |
          v
 recommendation_generation
          |
          v
 evidence_validation
       /        \
    valid       invalid
      |            |
      v            v
 format       refine_response
 response          |
      |            v
     END     evidence_validation
```

------------------------------------------------------------------------

# 8. Retrieval Implementation

Implement:

``` python
async def hybrid_search(
    query: str,
    environmental_context: dict,
    intent: dict,
    top_k: int = 10,
) -> list[dict]:
    ...
```

Use the same 2048-dimensional embedding model as ingestion.

Initial candidate configuration:

``` env
VECTOR_TOP_K=20
STRUCTURED_TOP_K=20
RELATIONSHIP_TOP_K=10
FINAL_EVIDENCE_COUNT=10
```

Hybrid score:

``` text
0.55 vector relevance
0.20 variable match
0.10 intervention match
0.10 context match
0.05 evidence quality
```

Make weights configurable.

------------------------------------------------------------------------

# 9. Vector Retrieval

Create a Supabase/pgvector RPC function if one does not already exist.

Concept:

``` sql
match_document_chunks(
    query_embedding,
    match_count,
    filters
)
```

Do not load all embeddings into Python.

Perform similarity search in PostgreSQL.

------------------------------------------------------------------------

# 10. Structured Retrieval

Use metadata from:

``` text
document_chunks
documents
research_observations
metric_relationships
```

Filter/prioritize using:

``` text
variables
topics
interventions
geographic_scope
climate_zones
evidence_level
```

Do not over-filter.

Global evidence can remain relevant when local evidence is unavailable.

------------------------------------------------------------------------

# 11. Evidence Provenance

Every evidence item must preserve:

``` json
{
  "chunk_id": "",
  "document_id": "",
  "title": "",
  "authors": [],
  "publication_year": null,
  "page_start": null,
  "page_end": null,
  "doi": "",
  "source_url": "",
  "content": "",
  "claims": [],
  "variables": []
}
```

The final response must be able to identify exactly which document/chunk
supports a recommendation.

------------------------------------------------------------------------

# 12. FastAPI API

Implement:

``` http
POST /api/chat
```

Request:

``` json
{
  "conversation_id": null,
  "message": "Biodiversity is declining on my farm",
  "environment": {
    "rainfall": 700,
    "soil_organic_carbon": 0.35,
    "land_use": "cropland"
  },
  "location": {
    "latitude": 19.03,
    "longitude": 73.02
  }
}
```

Response:

``` json
{
  "conversation_id": "",
  "answer": "",
  "clarification_required": false,
  "recommendations": [],
  "evidence": []
}
```

Use Pydantic schemas.

------------------------------------------------------------------------

# 13. Next.js Frontend

Build a clean chat interface.

Required:

-   chat messages
-   loading state
-   conversation persistence
-   environmental context input
-   optional location
-   recommendation cards
-   impacted metric display
-   evidence/source display
-   confidence
-   time horizon
-   clarification questions

The frontend must call FastAPI.

Do not put scientific reasoning in Next.js.

------------------------------------------------------------------------

# 14. Environment Variables

Create `.env.example`.

Include:

``` env
LLM_PROVIDER=openrouter

OPENROUTER_API_KEY=
OPENROUTER_LLM_MODEL=google/gemma-4-31b-it
OPENROUTER_EMBEDDING_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free

NVIDIA_API_KEY=
NVIDIA_MODEL=google/gemma-4-31b-it

GOOGLE_API_KEY=
GOOGLE_MODEL=gemma-4-31b-it

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

VECTOR_TOP_K=20
STRUCTURED_TOP_K=20
RELATIONSHIP_TOP_K=10
FINAL_EVIDENCE_COUNT=10

VECTOR_WEIGHT=0.55
VARIABLE_WEIGHT=0.20
INTERVENTION_WEIGHT=0.10
CONTEXT_WEIGHT=0.10
EVIDENCE_WEIGHT=0.05
```

Never expose:

``` text
SUPABASE_SERVICE_ROLE_KEY
```

to the browser.

------------------------------------------------------------------------

# 15. LLM Provider Abstraction

Create one service:

``` python
generate_text(...)
generate_structured(...)
```

Provider switching must happen through:

``` env
LLM_PROVIDER=openrouter
```

or:

``` env
LLM_PROVIDER=nvidia
```

or:

``` env
LLM_PROVIDER=google
```

Do not duplicate provider logic across LangGraph nodes.

------------------------------------------------------------------------

# 16. Error Handling

Handle:

-   LLM timeout
-   rate limits
-   invalid JSON
-   Supabase errors
-   vector search failure
-   empty retrieval
-   insufficient evidence

Never fabricate an answer because retrieval failed.

If evidence is insufficient:

``` json
{
  "answer": "I don't have enough evidence in the current knowledge base to make a reliable recommendation.",
  "clarification_required": true
}
```

------------------------------------------------------------------------

# 17. Testing

Create tests for:

### Query understanding

-   biodiversity question
-   soil question
-   incomplete query

### Context checking

-   sufficient context
-   missing context

### Retrieval

-   vector search
-   structured search
-   hybrid ranking
-   deduplication

### Evidence validation

-   supported claim
-   unsupported claim
-   unsupported number
-   mismatched condition

### Graph

-   clarification branch
-   successful recommendation branch
-   validation/refinement branch

### API

-   valid request
-   invalid request
-   empty message

------------------------------------------------------------------------

# 18. Observability

Log:

``` text
conversation_id
node
latency
retrieval count
selected evidence
validation status
```

Do not log:

``` text
API keys
service-role keys
private credentials
unnecessary sensitive user information
```

------------------------------------------------------------------------

# 19. Implementation Order

Follow this order.

### Phase 1

Inspect the existing repository.

Do not overwrite working code.

Identify:

``` text
existing Supabase schema
existing environment variables
existing embedding utilities
existing project structure
```

### Phase 2

Implement:

``` text
Supabase client
LLM provider abstraction
embedding query service
```

### Phase 3

Implement:

``` text
vector retrieval
structured retrieval
hybrid retrieval
```

### Phase 4

Implement LangGraph:

``` text
state
nodes
edges
conditional routing
```

### Phase 5

Implement:

``` text
FastAPI /api/chat
```

### Phase 6

Implement:

``` text
Next.js chat UI
```

### Phase 7

Add:

``` text
evidence validation
conversation persistence
logging
tests
```

------------------------------------------------------------------------

# 20. Critical Constraints

Do NOT build a generic ReAct agent that blindly calls tools.

Do NOT allow the LLM to decide scientific facts without evidence.

Do NOT generate recommendations before retrieval.

Do NOT use only vector similarity.

Do NOT use only structured filtering.

Do NOT treat research observations as current user measurements.

Do NOT invent numerical effects.

Do NOT cite documents that were not retrieved.

Do NOT hide evidence provenance.

Do NOT create a single giant LangGraph node.

Do NOT use JavaScript/TypeScript LangGraph.

The backend LangGraph implementation MUST be Python.

------------------------------------------------------------------------

# 21. Acceptance Criteria

The implementation is complete only when this flow works:

``` text
Next.js
  |
  v
POST /api/chat
  |
  v
FastAPI
  |
  v
LangGraph
  |
  v
Query understanding
  |
  v
Context validation
  |
  +---- missing ----> clarification
  |
  v
Context builder
  |
  v
Hybrid retrieval
  |
  v
Evidence aggregation
  |
  v
Multi-metric reasoning
  |
  v
Recommendation generation
  |
  v
Evidence validation
  |
  +---- unsupported --> refinement
  |
  v
Structured response
  |
  v
Next.js
```

Test with at least these scenarios:

### Scenario A

``` text
"Biodiversity is declining."
```

Expected:

``` text
clarification question
```

### Scenario B

``` text
"My cropland receives about 700 mm rainfall,
soil organic carbon is 0.35%, and biodiversity is declining."
```

Expected:

``` text
hybrid retrieval
multi-metric reasoning
specific recommendation
evidence
metrics
time horizon
```

### Scenario C

Ask a question requiring a numerical claim.

Expected:

``` text
The system only gives a number when the retrieved evidence
explicitly contains that number.
```

### Scenario D

Force retrieval to return insufficient evidence.

Expected:

``` text
No fabricated scientific recommendation.
```

------------------------------------------------------------------------

# 22. Developer Deliverables

Produce:

``` text
backend/
frontend/
README.md
.env.example
tests/
```

README must explain:

1.  Architecture
2.  LangGraph workflow
3.  Hybrid retrieval
4.  Supabase schema usage
5.  Environment setup
6.  Running locally
7.  API endpoint
8.  Frontend setup
9.  Testing
10. Deployment

Before finishing:

1.  Run backend tests.
2.  Run frontend checks.
3.  Start FastAPI.
4.  Start Next.js.
5.  Test `/api/chat`.
6.  Verify Supabase retrieval.
7.  Verify evidence citations.
8.  Verify clarification flow.
9.  Verify evidence validation.
10. Report any unresolved issues.

Do not claim completion unless the implementation has actually been
tested.
