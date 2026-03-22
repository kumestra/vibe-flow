# RAG (Retrieval-Augmented Generation) Learning Notes

## 1. What Is RAG?

RAG gives an LLM the ability to access external data sources to answer questions. Instead of relying solely on what the model learned during training, the system retrieves relevant information from a knowledge base and includes it in the prompt.

## 2. When to Use RAG (and When Not To)

If your data is small enough to fit in the LLM's context window, you often don't need RAG. You can simply paste the entire document into the prompt — this is called **context stuffing**, and it's simpler to build and debug.

RAG becomes worth it when:

- **Data is too large for the context window** — thousands of documents, a full knowledge base, or a codebase.
- **Data changes frequently** — product inventory, support tickets, news. RAG lets you update a search index independently without re-embedding everything into a prompt.
- **Cost and latency matter** — sending 100k tokens every request is slow and expensive. RAG lets you send only the 2–3 relevant chunks.
- **Precision matters** — LLMs can "lose" information buried in long contexts (the "lost in the middle" problem). Retrieving just the most relevant passages can give better answers.

**Rule of thumb:**

| Scenario | Approach |
|---|---|
| Small, static data (a few pages) | Put it in the prompt |
| Large, dynamic, or cost-sensitive | Use RAG |

## 3. The Core RAG Pipeline

The basic pipeline has three steps:

```
User Question
     │
     ├──→ [Query Formulation] ──→ [Retriever] ──→ Retrieved Chunks
     │                                               │
     └───────────────────────────┬───────────────────┘
                                 │
                          [LLM Prompt: Question + Chunks]
                                 │
                              Answer
```

1. **Query formulation** — transform the user's question into something suitable for searching. The raw question sometimes works, but often needs rewriting (expanding abbreviations, resolving pronouns, rephrasing for better search).
2. **Retrieval** — search the knowledge base and pull back the most relevant chunks. This can be vector search (semantic similarity), keyword search (BM25), or hybrid.
3. **Generation** — combine the original question + retrieved chunks into a prompt, send to the LLM, get the answer.

**Important nuance:** the query sent to the retriever and the question sent to the LLM are not always the same. The retrieval query is optimized for *search*; the LLM prompt is optimized for *answering*.

## 4. Routing: Deciding If Retrieval Is Needed

Not every user message needs retrieval. If a user says "hello," there's nothing to search for. Production systems handle this with multiple approaches:

### Intent Classification / Router

Classify the message before retrieval:

```python
def needs_retrieval(user_message: str) -> bool:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": user_message}],
        system="""Decide if this message requires looking up external
        information to answer. Reply with only YES or NO.

        Examples that do NOT need retrieval: greetings, casual chat,
        opinions, simple math.
        Examples that DO need retrieval: questions about specific
        products, policies, documents, facts."""
    )
    return "YES" in response.content[0].text
```

### Always Retrieve, Let the LLM Ignore Irrelevant Results

Run retrieval on everything. Include a system prompt instruction: "Use the provided context only if relevant. Otherwise, respond naturally." Simple to build, but wastes time on unnecessary retrieval.

### Relevance Score Threshold

Run retrieval, but filter results by similarity score:

```python
results = vector_store.similarity_search_with_score(query, k=3)

relevant_chunks = [doc for doc, score in results if score >= 0.75]

if relevant_chunks:
    # build prompt with chunks
else:
    # let LLM answer directly without context
```

### Production Approach: Combine Multiple Strategies

```
User Message
     │
     ▼
[Quick Rule Check] ──→ Obviously no retrieval needed ──→ LLM answers directly
     │
     ▼ (ambiguous)
[Router: needs retrieval?]
     │
     ├── NO ──→ LLM answers directly
     │
     ├── YES
     │    │
     │    ▼
     │  [Retriever] ──→ results with scores
     │    │
     │    ├── All scores below threshold ──→ LLM answers without context
     │    │
     │    └── Some scores above threshold ──→ LLM answers with those chunks
     │
     ▼
  Final Answer
```

The router doesn't have to be a full LLM call. Options from fastest to most accurate:

| Approach | Speed | Accuracy |
|---|---|---|
| Rule-based (keyword matching, message length) | Fastest | Rough |
| Small classifier model (fine-tuned BERT, etc.) | Fast | Good |
| LLM call | Slowest | Best |

## 5. Embeddings

### What Is an Embedding?

An embedding converts text into a list of numbers (a vector) that captures its meaning:

```
"how to reset my password"  →  [0.021, -0.43, 0.87, ..., 0.15]
                                  (typically 768–3072 numbers)
```

Texts with similar meanings end up with similar vectors, which is what makes vector search possible.

### Embedding Models

An embedding model is a different model from the LLM you chat with. Common options:

| Model | Dimensions | Provider |
|---|---|---|
| `text-embedding-3-small` | 1536 | OpenAI |
| `text-embedding-3-large` | 3072 | OpenAI |
| `voyage-3` | 1024 | Voyage AI |
| `all-MiniLM-L6-v2` | 384 | Open source (runs locally) |

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="how to reset my password"
)

vector = response.data[0].embedding
# [0.021, -0.43, 0.87, ..., 0.15]  — 1536 numbers
```

### Critical Rule

The **same** embedding model must be used for both storing documents and querying. You cannot embed documents with one model and search with another — their vectors exist in different spaces.

### Embedding User Queries

At query time, the user's message goes through the same embedding model:

```python
# At indexing time (documents)
doc_vector = embed("Our return policy allows 30-day returns for all items.")
vector_db.store(doc_vector, text=doc_text)

# At query time (user prompt)
query_vector = embed("can I return something I bought last week?")
results = vector_db.similarity_search(query_vector, k=3)
```

Raw user prompts often make poor search queries. Query rewriting improves results:

```python
def rewrite_query(user_message: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": user_message}],
        system="""Rewrite this user message into a clear, concise
        search query for finding relevant documents.
        Output only the rewritten query, nothing else."""
    )
    return response.content[0].text

raw = "hey so I bought this thing and it broke after like 2 days, what can I do?"
rewritten = rewrite_query(raw)
# → "product warranty claim defective item return policy"
```

In multi-turn conversations, resolve the query against chat history first:

```python
chat_history = [
    {"role": "user", "content": "what is your return policy?"},
    {"role": "assistant", "content": "We offer 30-day returns..."},
    {"role": "user", "content": "what about electronics?"},
]

def resolve_query(chat_history: list) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        messages=chat_history,
        system="""Given the conversation, rewrite the user's latest
        message as a standalone search query that captures the full
        intent. Output only the query."""
    )
    return response.content[0].text

# → "return policy for electronics"
```

## 6. The Ingestion Pipeline

Before retrieval can happen, documents must be processed and stored:

```
Raw Documents
     │
     ▼
[Chunking] ──→ Split into smaller pieces
     │
     ▼
[Embedding] ──→ Convert each chunk into a vector
     │
     ▼
[Storing] ──→ Save vectors + original text into vector DB
```

## 7. Chunking Best Practices

### Chunk Size

| Chunk size | Good for | Bad for |
|---|---|---|
| ~128 tokens | FAQ, short factual lookups | Long explanations, narrative text |
| ~256–512 tokens | General-purpose (most common) | Very structured data |
| ~1024+ tokens | Long-form documents, legal, research papers | Precise factual retrieval |

**Start with 256–512 tokens. Adjust based on results.**

### Overlap

Chunks should overlap so meaning isn't lost at boundaries. 10–20% overlap is typical:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

chunks = splitter.split_text(document_text)
```

### Split on Natural Boundaries

Don't cut every N characters. `RecursiveCharacterTextSplitter` tries to split in priority order:

1. Paragraph breaks (`\n\n`)
2. Line breaks (`\n`)
3. Sentences (`. `)
4. Words (` `)
5. Characters (last resort)

For Markdown documents:

```python
from langchain.text_splitter import MarkdownTextSplitter

splitter = MarkdownTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
```

### Keep Metadata with Each Chunk

Always store where a chunk came from:

```python
chunks_with_metadata = []
for i, chunk in enumerate(chunks):
    chunks_with_metadata.append({
        "text": chunk,
        "source": "user_manual_v2.pdf",
        "page": 14,
        "section": "Account Settings",
        "chunk_index": i,
    })
```

### Different Data Types Need Different Strategies

| Data type | Strategy |
|---|---|
| Prose / articles | Recursive text splitter, 256–512 tokens |
| Markdown / docs | Split by headers, then by size |
| Code | Split by functions/classes, not arbitrary lines |
| Tables / CSV | Keep each row or logical group as one chunk |
| Q&A pairs | Each Q+A pair is one chunk — don't split them |
| Legal contracts | Split by clause/section |

### Advanced: Parent-Child Chunking

Use small chunks for precise retrieval, but return the larger surrounding context to the LLM:

```
Document
  └── Parent chunk (2000 tokens) ← sent to LLM
        ├── Child chunk (200 tokens) ← used for search
        ├── Child chunk (200 tokens)
        └── Child chunk (200 tokens)
```

```python
# Pseudocode
small_chunks = split(document, size=200)
for chunk in small_chunks:
    store_in_vector_db(
        text=chunk,
        embedding=embed(chunk),
        metadata={"parent_id": parent_chunk_id}
    )

# At retrieval time:
matched_child = vector_db.search(query)
parent = get_parent(matched_child.metadata["parent_id"])
# Send parent (larger context) to the LLM
```

## 8. Vector Databases

### Purpose-Built Vector Databases

| | Pinecone | Weaviate | Qdrant | Milvus | Chroma |
|---|---|---|---|---|---|
| **Hosting** | Fully managed (cloud only) | Self-hosted or cloud | Self-hosted or cloud | Self-hosted or cloud (Zilliz) | Self-hosted or embedded |
| **Language** | Closed source | Go | Rust | Go/C++ | Python |
| **Hybrid search** | Yes | Yes (BM25 built-in) | Yes (sparse vectors) | Yes | No |
| **Filtering** | Metadata filters | Metadata + GraphQL | Rich metadata filters | Metadata filters | Basic metadata filters |
| **Scale** | Billions of vectors | Millions–billions | Millions–billions | Billions | Thousands–millions |
| **Best for** | Zero ops | Hybrid out of the box | Performance, self-hosted | Very large scale | Prototyping, small projects |
| **Ease of setup** | Easiest (SaaS) | Moderate | Moderate | Complex | Easiest (in-process) |
| **Pricing** | Pay-per-use | Free self-hosted, paid cloud | Free self-hosted, paid cloud | Free self-hosted, paid via Zilliz | Free / open source |

### Traditional DBs with Vector Support

| | PostgreSQL + pgvector | Redis + RediSearch | Elasticsearch |
|---|---|---|---|
| **Best for** | Already using Postgres | Already using Redis | Strong hybrid search |
| **Hybrid search** | Yes (with full-text search) | Yes | Yes (best-in-class BM25 + vector) |
| **Scale** | Millions | Millions | Millions–billions |
| **Trade-off** | Not optimized for vector-only | Data must fit in memory | Heavier to operate |

### How to Choose

- **Prototyping** → Chroma
- **Small team, no ops** → Pinecone
- **Need hybrid search** → Weaviate or Elasticsearch
- **Performance and control** → Qdrant
- **Massive scale (100M+ vectors)** → Milvus
- **Already running Postgres** → pgvector

## 9. Hybrid Search

Vector search alone can struggle with:

- **Exact keyword matches** — error codes like `ERR_4092`, product names
- **Structured filters** — "results from the 2025 manual only"

Hybrid search combines vector search with keyword search (BM25):

```python
# Pseudocode: hybrid retrieval
vector_results = vector_db.similarity_search(query_embedding, k=5)
keyword_results = keyword_index.search(query_text, k=5)

# Merge and re-rank
final_results = rerank(vector_results + keyword_results, query_text)
```

### Elasticsearch for Hybrid Search

Elasticsearch supports both BM25 and vector search natively:

```python
query = {
    "query": {
        "bool": {
            "should": [
                {"match": {"content": "how to reset password"}}
            ]
        }
    },
    "knn": {
        "field": "content_embedding",
        "query_vector": query_embedding,
        "k": 5,
        "num_candidates": 50
    },
    "rank": {
        "rrf": {}  # Reciprocal Rank Fusion
    }
}
```

Other options for the keyword side: OpenSearch, Typesense, Meilisearch, PostgreSQL full-text search.

**Industry trend:** tools are converging. Elasticsearch added vectors. Vector DBs are adding keyword search. The market is moving toward single systems that handle both.

## 10. Performance and Latency

Every RAG step adds latency:

```
Step                          Time
─────────────────────────────────────
Router (need retrieval?)      ~500-1000ms  (LLM call)
Query rewriting               ~500-1000ms  (LLM call)
Embedding the query           ~50-200ms    (API call)
Vector DB search              ~10-100ms    (fast)
Re-ranking results            ~200-500ms   (if used)
Final LLM generation          ~1000-3000ms (LLM call)
─────────────────────────────────────
Total                         ~2-6 seconds
```

A simple LLM call without RAG: ~1–3 seconds. RAG can roughly double response time.

### Optimization Strategies

**Run steps in parallel:**

```python
import asyncio

async def rag_pipeline(user_message: str):
    needs_rag, rewritten_query = await asyncio.gather(
        check_needs_retrieval(user_message),
        rewrite_query(user_message),
    )

    if not needs_rag:
        return await generate_answer(user_message, context=None)

    query_vector = await embed(rewritten_query)
    results = await vector_db.search(query_vector)
    return await generate_answer(user_message, context=results)
```

**Eliminate unnecessary steps:**

| Step | Skip it when... |
|---|---|
| Router | Your app always needs retrieval (e.g., docs Q&A bot) |
| Query rewriting | Queries are already clear and single-turn |
| Re-ranking | Retrieval quality is already good enough |

A minimal pipeline is just: **embed → search → generate**.

**Use smaller models for intermediate steps:**

```python
# Fast, cheap model for routing
router_response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    ...
)

# Best model for the final answer
answer = client.messages.create(
    model="claude-sonnet-4-6",
    ...
)
```

**Stream the final response:**

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": prompt_with_context}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**Cache at every layer:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embed(text: str):
    return embed(text)
```

### Realistic Latency

| Setup | Latency | When to use |
|---|---|---|
| Minimal (embed → search → generate + streaming) | ~1.5–2.5s to first token | Most applications |
| Full pipeline (router, rewrite, rerank) | ~3–6s to first token | Quality must be maximized |
| Optimized (caching + parallel + fast models) | ~1–2s to first token | Tuned production systems |

## 11. RAG Frameworks and Tools

### Frameworks (for developers)

| Project | What it is |
|---|---|
| **LangChain** (100k+ stars) | Most popular. Building blocks for every part of the RAG pipeline. Python and JS. |
| **LlamaIndex** (40k+ stars) | Focused on connecting LLMs with data. More opinionated, easier to get started. |
| **Haystack** (18k+ stars) | Production-oriented. Strong on hybrid search and Elasticsearch. |

### Open Source RAG Applications (ready to use)

| Product | What it does |
|---|---|
| **Onyx** (formerly Danswer) | Workplace search — connects to Slack, Google Drive, Confluence, etc. |
| **PrivateGPT** | Chat with documents, runs 100% locally. |
| **Quivr** | "Second brain" — upload docs, chat with them via web UI. |
| **RAGFlow** (30k+ stars) | Document Q&A with deep parsing, visual UI. |
| **Anything LLM** | Desktop app — drag and drop documents, supports local LLMs. |
| **Khoj** | Personal AI assistant with RAG over notes and documents. |
| **Perplexica** | Open source Perplexity alternative — RAG over the internet. |
| **LibreChat** | ChatGPT-like UI with file uploads and RAG. |

Easiest to self-host: **Anything LLM** (desktop, no Docker), **PrivateGPT** (fully local), **Onyx** (Docker Compose).

### Commercial RAG Products

| Product | What it does |
|---|---|
| **ChatGPT** (file upload / GPTs) | Upload files, ask questions. Custom GPTs with permanent knowledge bases. |
| **Claude** (Projects) | Upload files to a Project, answers based on them. |
| **Google NotebookLM** | Upload documents, generates summaries, Q&A, podcasts. |
| **Perplexity** | RAG over the live internet with citations. |
| **Glean** | Enterprise workplace search across all company tools. |
| **Notion AI** | RAG over your Notion workspace. |
| **Harvey** | Legal domain — RAG over case law and contracts. |
| **Consensus** | Academic domain — RAG over scientific papers. |

Most AI products that claim to "know your data" or "answer with citations" are RAG applications behind a UI.

## 12. Building a Mini RAG for Learning

To verify your RAG is working, use data the LLM doesn't already know:

**Best approach: make up fake documents.**

```python
documents = [
    "VibeFlow Inc. was founded in 2024. The CEO is Jane Zhao.",
    "VibeFlow's return policy: 45-day returns on all items except custom orders.",
    "VibeFlow's enterprise plan costs $299/month and includes up to 50 users.",
    "To reset your VibeFlow password, go to Settings > Security > Reset.",
    "VibeFlow's API rate limit is 1000 requests per minute on the pro plan.",
]
```

**How to verify it works:**

1. Ask **with** retrieval → should answer correctly
2. Ask **without** retrieval → should say "I don't know" or hallucinate

If both happen, your RAG is doing its job.

**Other good data sources for learning:**

- Your own personal notes or documents
- Very recent data (after the LLM's knowledge cutoff)
- Niche/obscure content the LLM is unlikely to have memorized
