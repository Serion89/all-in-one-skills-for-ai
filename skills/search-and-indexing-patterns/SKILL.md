---
name: search-and-indexing-patterns
description: Full-text search, inverted indexing, and search engine integration. Use when designing search schemas in Elasticsearch, Meilisearch, or PostgreSQL Full-Text Search, tuning BM25 relevance scoring, faceted filtering, and zero-downtime reindexing.
---

# Search Architecture & Inverted Indexing Patterns

## Purpose
Design resilient, high-speed full-text and faceted search systems using inverted indices, Elasticsearch, Meilisearch, and PostgreSQL Full-Text Search (FTS).

---

## Core Search Architectural Patterns

### 1. PostgreSQL Native Full-Text Search (Small-to-Medium Datasets)
Before deploying dedicated search clusters, leverage native PostgreSQL `tsvector` and `tsquery` with GIN indexing:
```sql
-- Add generated tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector
GENERATED ALWAYS AS (
  setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(body, '')), 'B')
) STORED;

-- Create GIN index for sub-millisecond retrieval
CREATE INDEX articles_search_idx ON articles USING gin(search_vector);

-- Query with BM25-like rank ordering
SELECT id, title, ts_rank_cd(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'distributed & systems') query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

### 2. Zero-Downtime Index Aliasing (Elasticsearch / OpenSearch)
Never point client applications directly to raw index names:
- Direct all read/write traffic to an **alias** (e.g. `products_search`).
- To reindex with new tokenizers or schema changes:
  1. Create new index `products_v2`.
  2. Populate `products_v2` in the background.
  3. Atomically switch the alias from `products_v1` to `products_v2` in a single API call:
     ```json
     {
       "actions": [
         { "remove": { "index": "products_v1", "alias": "products_search" } },
         { "add":    { "index": "products_v2", "alias": "products_search" } }
       ]
     }
     ```
  4. Delete old index `products_v1` once traffic is verified stable.

### 3. Relevance Tuning & Typo Tolerance Heuristics
- **Faceted Filters**: Isolate attributes into exact keyword fields (e.g. `category.keyword`, `brand.keyword`).
- **N-gram Tokenizers**: Use edge n-grams for instant autocomplete as users type.
- **Fuzzy Search Bounds**: Cap Levenshtein edit distance at 1 for words $\le 4$ characters, and max 2 for longer words to prevent false-positive result noise.
