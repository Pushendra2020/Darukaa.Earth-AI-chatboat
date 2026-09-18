# Darukaa.Earth

## Next.js → FastAPI → LangGraph System Flow

## 1. Overall Architecture

``` text
┌──────────────────────────────────────────────┐
│                  Next.js                     │
│                                              │
│  Chat UI                                     │
│  Environment Input                           │
│  Location Input                              │
│  Conversation State                          │
└───────────────────┬──────────────────────────┘
                    │ HTTPS
                    │ POST /api/chat
                    v
┌──────────────────────────────────────────────┐
│                FastAPI                       │
│                                              │
│  API validation                              │
│  Authentication                              │
│  Request normalization                       │
│  Conversation ID                             │
└───────────────────┬──────────────────────────┘
                    │
                    v
┌──────────────────────────────────────────────┐
│              LangGraph                       │
│                                              │
│  Query Understanding                         │
│  Context Check                               │
│  Context Builder                             │
│  Hybrid Retrieval                            │
│  Evidence Aggregation                        │
│  Multi-Metric Reasoning                      │
│  Recommendation Generation                   │
│  Evidence Validation                         │
└───────────────────┬──────────────────────────┘
                    │
          ┌─────────┼──────────┐
          │         │          │
          v         v          v
      Supabase   Vector DB   LLM Provider
      Database   pgvector    Configurable
          │
          v
   Knowledge Base
```

------------------------------------------------------------------------

# 2. Frontend Request

The user interacts with the Next.js application.

Example:

``` text
User:
"My farm has lower biodiversity than before.
The soil is becoming dry."
```

The frontend creates:

``` json
{
  "conversation_id": "uuid",
  "message": "My farm has lower biodiversity than before. The soil is becoming dry.",
  "environment": {},
  "location": null
}
```

Send:

``` http
POST /api/chat
Content-Type: application/json
```

------------------------------------------------------------------------

# 3. FastAPI Request Model

Recommended Pydantic model:

``` python
class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str
    environment: dict | None = None
    location: dict | None = None
```

FastAPI should:

1.  Validate the request.
2.  Create a conversation ID if needed.
3.  Normalize optional environmental data.
4.  Invoke the LangGraph service.
5.  Return the graph result.

------------------------------------------------------------------------

# 4. FastAPI Should Not Contain AI Logic

Avoid:

``` python
@app.post("/chat")
async def chat(request):
    # huge LLM prompt
    # retrieval
    # database queries
    # reasoning
    # validation
```

Instead:

``` python
@app.post("/api/chat")
async def chat(request: ChatRequest):

    result = await graph_service.run(
        conversation_id=request.conversation_id,
        message=request.message,
        environment=request.environment,
        location=request.location,
    )

    return result
```

This keeps the API layer clean.

------------------------------------------------------------------------

# 5. LangGraph Invocation

FastAPI passes normalized input to LangGraph:

``` python
initial_state = {
    "conversation_id": conversation_id,
    "user_query": request.message,
    "environmental_context": request.environment or {},
    "messages": []
}

result = await graph.ainvoke(initial_state)
```

For streaming UX, use LangGraph streaming and expose the events through
an appropriate FastAPI streaming endpoint.

------------------------------------------------------------------------

# 6. Conversation Flow

Conversation example:

### Turn 1

``` text
User:
"Biodiversity is declining on my farm."
```

Graph determines that important context is missing.

Response:

``` text
"To understand the likely drivers, what are the approximate
annual rainfall, land use, and soil organic carbon conditions?"
```

### Turn 2

``` text
User:
"Rainfall is around 700 mm, it's cropland, and soil organic
carbon is about 0.35%."
```

The same `conversation_id` is sent.

FastAPI loads the conversation.

LangGraph combines:

``` text
previous conversation
+
new user message
+
new environmental measurements
```

Then proceeds to retrieval and reasoning.

------------------------------------------------------------------------

# 7. Frontend Conversation State

Next.js should maintain:

``` text
conversation_id
messages
current_environment
location
loading state
streaming state
```

The backend should remain the source of truth for scientific reasoning
and conversation persistence.

The frontend should not independently calculate environmental
recommendations.

------------------------------------------------------------------------

# 8. Recommended Frontend Response

``` json
{
  "conversation_id": "uuid",
  "answer": "The current combination of low soil organic carbon...",
  "recommendations": [
    {
      "action": "Introduce...",
      "why_it_works": "...",
      "impacted_metrics": [
        "soil_organic_carbon",
        "soil_moisture",
        "habitat_diversity"
      ],
      "time_horizon": "1-3 years",
      "confidence": 0.84,
      "evidence": [
        {
          "document_id": "...",
          "title": "...",
          "year": 2022,
          "pages": "10-14"
        }
      ]
    }
  ],
  "clarification_required": false
}
```

------------------------------------------------------------------------

# 9. UI Rendering

The frontend should visually separate:

### Answer

Natural-language explanation.

### Recommendations

Each recommendation is a separate card.

### Impacted metrics

Example:

``` text
Soil organic carbon     ↑
Soil moisture           ↑
Habitat diversity       ↑
```

### Evidence

Show:

``` text
Source
Publication year
Relevant page
Evidence statement
```

### Confidence

Show confidence only as a supporting signal, not as proof that the
scientific claim is true.

------------------------------------------------------------------------

# 10. Error Flow

``` text
Next.js
   |
   v
FastAPI
   |
   v
LangGraph
   |
   +---- LLM failure --------> retry/fallback
   |
   +---- Retrieval failure --> return controlled error
   |
   +---- Validation failure -> refine
   |
   v
Response
```

The backend must never return fabricated scientific evidence because a
provider failed.

------------------------------------------------------------------------

# 11. Suggested Backend Structure

``` text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── chat.py
│   │
│   ├── schemas/
│   │   └── chat.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── graph.py
│   │   └── nodes/
│   │       ├── conversation.py
│   │       ├── query_understanding.py
│   │       ├── context.py
│   │       ├── retrieval.py
│   │       ├── evidence.py
│   │       ├── reasoning.py
│   │       ├── recommendation.py
│   │       └── validation.py
│   │
│   ├── retrieval/
│   │   ├── vector.py
│   │   ├── structured.py
│   │   └── hybrid.py
│   │
│   ├── services/
│   │   ├── llm.py
│   │   ├── conversation.py
│   │   └── evidence_validator.py
│   │
│   └── db/
│       ├── supabase.py
│       └── queries.py
│
└── tests/
```

------------------------------------------------------------------------

# 12. Deployment Flow

``` text
User Browser
     |
     v
Next.js
     |
     v
FastAPI
     |
     v
LangGraph
     |
     +--------> Supabase
     |
     +--------> OpenRouter / other LLM provider
     |
     +--------> Embedding provider
```

The Next.js application should never receive the Supabase service-role
key.

The service-role key belongs only on the backend.

------------------------------------------------------------------------

# 13. Important Boundary

``` text
Next.js
   |
   | user interaction
   v
FastAPI
   |
   | orchestration request
   v
LangGraph
   |
   | reasoning + retrieval
   v
Knowledge Base
```

The frontend is the interface.

FastAPI is the API boundary.

LangGraph is the orchestration/reasoning workflow.

Supabase is the persistence and knowledge layer.
