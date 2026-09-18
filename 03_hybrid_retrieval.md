# Darukaa.Earth

## Hybrid Retrieval Architecture

## 1. Goal

The retrieval layer must combine:

1.  Semantic vector retrieval from `document_chunks`
2.  Structured retrieval/filtering from Supabase tables
3.  Environmental metric relationships
4.  Evidence metadata and provenance

The goal is not simply to find text that sounds similar.

The goal is to find evidence that is scientifically relevant to the
user's specific environmental context.

------------------------------------------------------------------------

# 2. Existing Knowledge Base

Primary tables:

``` text
documents
document_chunks
research_observations
metric_relationships
```

`document_chunks` contains:

-   content
-   embedding
-   document_id
-   chunk_index
-   page_start
-   page_end
-   topics
-   variables
-   interventions
-   claims

`documents` contains document-level metadata.

`research_observations` contains measurements explicitly reported in
research documents.

`metric_relationships` contains structured relationships such as:

``` text
rainfall
    -> affects
soil_moisture

soil_moisture
    -> affects
vegetation

vegetation
    -> affects
habitat_quality

habitat_quality
    -> affects
species_richness
```

------------------------------------------------------------------------

# 3. Retrieval Input

The retrieval node receives:

``` json
{
  "query": "Biodiversity is declining and soil is dry",
  "environment": {
    "soil_organic_carbon": 0.35,
    "soil_moisture": 15,
    "rainfall": 700,
    "land_use": "cropland"
  },
  "location": {
    "latitude": 19.03,
    "longitude": 73.02
  },
  "intent": {
    "goal": "improve_biodiversity"
  }
}
```

------------------------------------------------------------------------

# 4. Query Construction

Do not create only one query.

Construct multiple retrieval concepts.

Example:

``` text
Query A:
biodiversity decline cropland

Query B:
low soil organic carbon biodiversity

Query C:
soil moisture biodiversity agricultural systems

Query D:
landscape complexity species richness farmland
```

The query concepts should come from:

-   user intent
-   mentioned metrics
-   missing/known metrics
-   ecosystem
-   possible interventions
-   metric relationships

------------------------------------------------------------------------

# 5. Vector Retrieval

Generate an embedding for the semantic query.

Use the same embedding model used during ingestion:

``` text
nvidia/llama-nemotron-embed-vl-1b-v2:free
```

Then perform pgvector similarity search against:

``` text
document_chunks.embedding
```

Recommended initial retrieval:

``` text
top_k = 20
```

Do not immediately send all 20 chunks to the LLM.

------------------------------------------------------------------------

# 6. Structured Retrieval

Run structured queries based on the environmental context.

Examples:

### Variable matching

Find chunks whose metadata contains:

``` text
soil_organic_carbon
species_richness
soil_moisture
```

### Intervention matching

Find chunks tagged with:

``` text
agroforestry
cover_crops
landscape_complexity
```

### Geographic/context matching

Where appropriate, prioritize:

``` text
India
South Asia
tropical
semi-arid
arid
temperate
```

depending on the user's context.

Do not discard globally relevant evidence solely because it is not
local.

------------------------------------------------------------------------

# 7. Metadata Filtering

Structured filtering should consider:

``` text
variables
topics
interventions
ecosystems
climate_zones
geographic_scope
publication_year
evidence_level
```

A possible retrieval filter:

``` json
{
  "variables": [
    "soil_organic_carbon",
    "soil_moisture",
    "species_richness"
  ],
  "topics": [
    "biodiversity",
    "agroecosystems"
  ]
}
```

------------------------------------------------------------------------

# 8. Hybrid Score

Combine semantic and structured relevance.

Example:

``` text
hybrid_score =
    0.55 * vector_score
  + 0.20 * variable_match
  + 0.10 * intervention_match
  + 0.10 * context_match
  + 0.05 * evidence_quality
```

These weights are starting values, not scientific constants.

Make them configurable.

For example:

``` env
VECTOR_WEIGHT=0.55
VARIABLE_WEIGHT=0.20
INTERVENTION_WEIGHT=0.10
CONTEXT_WEIGHT=0.10
EVIDENCE_WEIGHT=0.05
```

------------------------------------------------------------------------

# 9. Why Hybrid Retrieval Matters

Vector search might retrieve:

``` text
"Agroforestry increases biodiversity..."
```

because it is semantically similar.

Structured retrieval can determine that the evidence also involves:

``` text
soil organic carbon
rainfall
agricultural land
species richness
```

This makes the result more useful for multi-metric reasoning.

------------------------------------------------------------------------

# 10. Metric Relationship Expansion

After identifying the user's primary metric, expand to related metrics.

Example:

``` text
User metric:
species_richness
```

Look up:

``` text
habitat_diversity
habitat_fragmentation
vegetation
soil_moisture
land_use
```

using `metric_relationships`.

This produces additional retrieval concepts.

Example:

``` text
species_richness
    |
    +--> habitat_diversity
    |
    +--> habitat_fragmentation
    |
    +--> vegetation
```

Then retrieve evidence related to these variables.

This is one of the mechanisms that prevents single-variable answers.

------------------------------------------------------------------------

# 11. Retrieval Pipeline

``` text
User Query
    |
    v
Query Understanding
    |
    v
Known Metrics
    |
    v
Metric Relationship Expansion
    |
    +-----------------------+
    |                       |
    v                       v
Vector Retrieval      Structured Retrieval
    |                       |
    |                       |
    +-----------+-----------+
                |
                v
          Candidate Pool
                |
                v
          Hybrid Scoring
                |
                v
          Deduplication
                |
                v
       Evidence Aggregation
                |
                v
         Top Evidence Set
```

------------------------------------------------------------------------

# 12. Candidate Pool

A reasonable starting point:

``` text
Vector retrieval:
20 candidates

Structured retrieval:
20 candidates

Relationship retrieval:
10 candidates

Combined:
up to 50 candidates
```

Then:

``` text
deduplicate
      ↓
hybrid score
      ↓
top 8-12 evidence items
```

The exact values should be configurable.

------------------------------------------------------------------------

# 13. Evidence Diversity

Do not select ten nearly identical chunks from the same paper.

Prefer evidence diversity across:

-   documents
-   interventions
-   environmental variables
-   ecosystem contexts

Example final evidence:

``` text
IPCC
   ↓
land-climate relationship

FAO
   ↓
soil health

Global meta-analysis
   ↓
landscape complexity

Agroforestry study
   ↓
soil carbon
```

This produces stronger multi-source reasoning.

------------------------------------------------------------------------

# 14. Evidence Provenance

Every retrieved evidence object should preserve:

``` json
{
  "chunk_id": "...",
  "document_id": "...",
  "content": "...",
  "title": "...",
  "authors": [],
  "publication_year": 2022,
  "page_start": 14,
  "page_end": 16,
  "doi": "...",
  "source_url": "...",
  "variables": [],
  "claims": []
}
```

Never strip provenance before sending evidence to the reasoning layer.

------------------------------------------------------------------------

# 15. Numerical Evidence

Numerical claims require special handling.

Example source:

``` text
Effect size: +18%
Metric: species richness
Intervention: landscape complexity
```

The recommendation generator may use:

``` text
18%
```

only if the retrieved evidence contains that value.

If the source contains no numerical effect:

``` text
effect_size = null
```

The final answer should not invent a number.

------------------------------------------------------------------------

# 16. Retrieval Function Interface

Recommended:

``` python
async def hybrid_search(
    query: str,
    environmental_context: dict,
    intent: dict,
    top_k: int = 10,
) -> list[dict]:
    ...
```

It should return normalized evidence objects, not raw database
responses.

------------------------------------------------------------------------

# 17. pgvector Search

Create a database function for vector similarity rather than pulling all
embeddings into Python.

Conceptually:

``` sql
match_document_chunks(
    query_embedding,
    match_count,
    filters
)
```

The function should return:

``` text
chunk
document metadata
similarity
```

Then combine those results with structured candidates in Python.

------------------------------------------------------------------------

# 18. Retrieval Failure Handling

If vector retrieval fails:

``` text
structured retrieval
+
known evidence
```

can still be used.

If structured retrieval fails:

``` text
vector retrieval
```

can still be used.

If both fail:

``` text
Do not fabricate an evidence-backed recommendation.
Return a controlled failure/insufficient-evidence response.
```

------------------------------------------------------------------------

# 19. Retrieval Quality Logging

For every query log:

``` text
conversation_id
query
vector_candidates
structured_candidates
relationship_candidates
final_evidence_count
selected_document_ids
retrieval_latency
```

This will be valuable during evaluation and debugging.

------------------------------------------------------------------------

# 20. Recommended Initial Configuration

``` env
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

Keep these configurable so retrieval can be tuned without rewriting the
graph.
