# Tech Stack and Design Stack: Premium RAG Chatbot

## Technical architecture stack

The architecture should separate ingestion, retrieval, orchestration, generation, storage, evaluation, and interface layers because enterprise RAG works best as a structured system rather than a single chat component [cite:18]. The recommended build is a RAG-first core with modular orchestration so the product can start narrow and expand cleanly [cite:19][cite:22].

## Recommended stack

| Layer | Recommendation | Why |
|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind CSS + Framer Motion | Strong app structure, premium UI, motion control, and maintainable component design. |
| Chat UI | Custom chat surface with citations, source drawer, answer cards | Internal assistants need trust-forward layouts, not generic chat clones. |
| API layer | FastAPI or Next.js Route Handlers | Strong Python compatibility for ML-heavy pipelines, or unified TS stack if preferred. |
| RAG framework | LlamaIndex first | LlamaIndex is optimized for RAG-first applications and stronger document retrieval defaults [cite:19][cite:2]. |
| Orchestration | LangChain or LangGraph for broader workflow logic | LangChain is stronger when the app grows beyond pure RAG into tools and multi-step workflows [cite:19][cite:22]. |
| Parsing | PyMuPDF, Unstructured, and optional LlamaParse | Complex document handling is a real differentiator for retrieval quality [cite:19]. |
| Embeddings | OpenAI text-embedding model or BGE/sentence-transformers | Start with quality embeddings and benchmark against cost. |
| Retrieval | Hybrid search + metadata filters + reranker | Enterprise RAG needs semantic plus literal search and reranking [cite:18]. |
| Vector store (prototype) | Chroma | Developer-friendly and suitable for prototypes or small-scale deployments [cite:3]. |
| Vector store (production) | Weaviate, Pinecone, or Qdrant | Better scale, filtering, and production readiness than Chroma at larger sizes [cite:17][cite:20][cite:3]. |
| Relational DB | PostgreSQL | Store users, permissions, audit logs, and app metadata. |
| Object storage | S3-compatible bucket | Store raw documents, parsed artifacts, and snapshots. |
| Auth | Clerk, Auth0, or internal SSO | Enterprise assistant must inherit organizational access rules. |
| Observability | Langfuse, OpenTelemetry, or LangSmith | Track traces, retrieval quality, and failures [cite:22][cite:19]. |
| Evaluation | RAGAS or custom evaluation suite | Production RAG needs test-set measurement, not demo intuition [cite:18]. |
| Deployment | Vercel for frontend, Railway/Render/Fly.io for backend, or cloud K8s later | Fast launch path with clean upgrade route. |

## Framework recommendation

For this project, LlamaIndex should own the ingestion and retrieval layer because it was built with RAG as its primary design center and usually ships document-heavy Q&A products faster with stronger defaults [cite:19][cite:2]. LangChain or LangGraph should be added only where broader workflow orchestration is needed, such as tool routing, agentic review, or external system actions [cite:19][cite:22].

This split is pragmatic rather than ideological. Many production stacks use LlamaIndex for retrieval and LangChain-family tooling for the wider application layer because the two ecosystems are complementary rather than mutually exclusive [cite:19].

## Vector database path

Chroma is the right prototype choice because it is developer-friendly and works well for small-scale or local experimentation [cite:3]. For a production rollout with larger corpora, filtering, concurrency, and SLA expectations, Weaviate, Pinecone, or Qdrant are stronger candidates because benchmark-style comparisons show much better query and indexing performance at larger scale than Chroma [cite:17][cite:20][cite:3].

Weaviate is attractive when hybrid search and structured filtering are priorities, Pinecone is attractive for managed simplicity, and Qdrant is attractive for strong filtered performance with lower operational cost profiles in some deployments [cite:17][cite:20][cite:3]. This means the architecture should keep vector-store adapters modular from day one.

## Retrieval design

The retrieval pipeline should follow this order: query intake, optional query rewrite, permission scope check, dense retrieval, keyword retrieval, merge, metadata filter, rerank, answer generation, and citation formatting [cite:18]. This ordering reflects the reality that fast first-pass retrieval is not enough; reranking and access scoping are necessary to make answers trustworthy [cite:18].

Recommended defaults for MVP:

- Chunk size strategy based on section-aware splitting, not raw token windows [cite:18].
- Parent-child retrieval so the system finds precise fragments but answers with sufficient surrounding context [cite:18].
- Top-k retrieval of 8 to 20 candidates before reranking, tuned during evaluation.
- Cross-encoder reranker for the final evidence shortlist.
- Citation anchors stored with document title, section title, and source URL or document path.

## Design stack

The design direction should be premium, editorial, and animated without looking like a generic neon AI product. A better visual reference is “executive intelligence dashboard meets refined product design” rather than “futuristic chatbot”.

### Visual principles

- Warm neutral surfaces with one strong accent color.
- Large, elegant typography for hero and dashboards.
- Crisp answer cards with subtle borders and layered depth.
- Motion used for continuity, not spectacle.
- High-trust answer zones with clear sources, timestamps, and status chips.

### UI stack

| Design layer | Recommendation | Why |
|---|---|---|
| Styling | Tailwind CSS with design tokens | Fast systemization and strong theming. |
| Animation | Framer Motion + subtle CSS transitions | Premium interaction quality for chat, drawers, and loading states. |
| Icons | Lucide | Clean, lightweight, modern UI language. |
| Charts | Recharts or lightweight Plotly views | Good for admin analytics and retrieval metrics. |
| Typography | Satoshi/General Sans for body + an elegant serif or display accent for headings | Creates premium contrast and avoids default-template feel. |

## Premium interaction ideas

- Animated answer reveal with staggered citation chips.
- Source drawer that slides in with highlighted supporting excerpts.
- Retrieval progress states such as “Searching policies”, “Reranking sources”, and “Drafting grounded answer”.
- Admin indexing dashboard with animated ingestion timeline and document health states.
- Query suggestions that morph based on department or role.

## Security and governance design

Enterprise RAG is only production-ready when permissions and governance are baked into the design, not bolted on later [cite:18]. The app should therefore visually expose role scope, source origin, restricted-content refusals, and answer provenance to reinforce trust at the interface layer [cite:18].

## Suggested repository structure

```text
rag-assistant/
  apps/
    web/
    admin/
  services/
    api/
    ingestion/
    evaluation/
  packages/
    ui/
    config/
    retrieval/
  infra/
    terraform/
  docs/
    prd/
    architecture/
```

## Implementation preference for this project

Given the requested premium animated experience, the strongest product combination is Next.js on the frontend, FastAPI for backend intelligence services, LlamaIndex for retrieval, PostgreSQL for app state, and a vector database abstraction that starts with Chroma and upgrades to Weaviate or Pinecone as the corpus grows [cite:19][cite:17][cite:20]. This stack balances rapid building with a clean path to enterprise-grade deployment.
