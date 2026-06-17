# Antigravity Prompt: Premium RAG Chatbot Over Company Documents

Use the following complete product documents as the source of truth to design and build the project. Treat them as authoritative requirements, architecture notes, and delivery workflow.

Your task is to create a premium, animated, enterprise-grade RAG chatbot over company documents. This is not a generic “chat with PDF” demo. It must be a high-trust internal knowledge assistant with structured ingestion, hybrid retrieval, reranking, citations, permission-aware access, evaluation, and workflow handoff.

## Primary objective
Build an internal AI assistant that answers questions over company documents using retrieval-augmented generation. The assistant must retrieve from approved company sources, generate grounded answers with citations, respect role-based permissions before retrieval and generation, and support downstream workflow actions such as task creation, summaries, or operational handoff.

## Product direction
- Position the product as a secure internal knowledge assistant, not a novelty chatbot.
- Optimize for speed plus trust: faster retrieval, consistent answers, citations, access control, and workflow follow-through.
- Start with one narrow, high-value pilot use case such as HR policy Q&A, onboarding knowledge, support knowledge, contract assistance, or sales enablement.
- Build for premium product quality with animated UI, polished empty states, refined loading states, source drill-down, and executive-grade visual design.

## Non-negotiable system principles
- Retrieval quality is more important than flashy generation.
- Ingestion quality determines downstream performance.
- Hybrid retrieval is mandatory: combine vector retrieval, keyword retrieval, metadata filtering, and reranking.
- Access control must be enforced before generation.
- All answers must be grounded in retrieved evidence and show citations.
- The system must abstain or qualify answers when evidence is weak, conflicting, or inaccessible.
- Evaluation is mandatory before rollout.
- Workflow automation comes after trusted retrieval quality is proven.

## Build requirements
Create the following system:

### 1. Ingestion layer
- Ingest PDF, DOCX, TXT, HTML, and knowledge-base exports.
- Parse, normalize, deduplicate, version, and tag every document.
- Preserve metadata such as source, owner, department, date, permission level, document version, and section hierarchy.
- Use source-aware parsing and document QA.
- Preserve section structure, clauses, headings, and tables where possible.

### 2. Indexing and retrieval layer
- Use section-aware chunking, not naive fixed splitting.
- Preserve parent-child context for retrieval.
- Build embeddings and store vectors in a modular vector store abstraction.
- Use hybrid retrieval with dense search plus sparse or keyword retrieval.
- Apply metadata filters before final answer context is assembled.
- Use reranking to improve final context quality.
- Tune top-k retrieval through evaluation, not guesswork.

### 3. Answer generation layer
- Generate answers only from approved retrieved context.
- Attach citations to sources.
- Separate answer text from evidence in the UI.
- Include uncertainty handling when evidence is incomplete.
- Refuse access to restricted content.

### 4. Permissions and governance
- Enforce role-based access and source-level permissions.
- Maintain audit logs.
- Respect sensitivity labels and restricted content rules.
- Ensure restricted data is never surfaced through retrieval or generation.

### 5. Workflow integration
- Support post-answer actions like drafting summaries, creating tasks, building reports, or handing off next actions.
- Treat workflow features as phase-two or phase-three capabilities after retrieval trust is validated.

### 6. Evaluation layer
- Measure context precision, context recall, answer faithfulness, answer relevance, citation quality, latency, and escalation behavior.
- Maintain a representative test set from real pilot queries.
- Log failures by root cause such as parsing failure, chunking failure, retrieval miss, reranking miss, or synthesis error.

## Recommended technical stack
Use this as the preferred implementation stack unless there is a strong reason to substitute:

- Frontend: Next.js + TypeScript + Tailwind CSS + Framer Motion
- Backend/API: FastAPI or Next.js route handlers
- RAG framework: LlamaIndex as the retrieval-first core
- Workflow orchestration: LangChain or LangGraph only where broader orchestration is needed
- Parsing: PyMuPDF, Unstructured, optional advanced parser if required
- Embeddings: high-quality embedding model, configurable for hosted or local usage
- Retrieval: hybrid search + metadata filters + reranker
- Prototype vector DB: Chroma
- Production vector DB path: Weaviate, Pinecone, or Qdrant via abstraction layer
- Relational DB: PostgreSQL for users, permissions, logs, and metadata
- Object storage: S3-compatible bucket for raw and parsed documents
- Auth: enterprise-ready auth or SSO-compatible design
- Observability: tracing and evaluation tooling

## Premium design brief
The UI must look premium, calm, intelligent, and enterprise-ready.

### Design language
- Avoid neon, purple-gradient, “AI template” aesthetics.
- Use warm neutral surfaces with one strong accent color.
- Use large elegant typography with refined hierarchy.
- Use subtle motion for continuity, not spectacle.
- Design crisp answer cards, source drawers, admin dashboards, and analytics views.
- Surface citations, source previews, confidence cues, timestamps, and permission states.
- Create polished empty states, loading states, and no-result flows.

### Key interface areas
- Landing or home view for internal assistant
- Chat interface with premium answer reveal
- Source citation chips and evidence drawer
- Document/source preview panel
- Admin indexing dashboard
- Evaluation and analytics dashboard
- Restricted-content and low-confidence response states

### Motion direction
- Animate answer reveal with staggered source chips.
- Add smooth drawer transitions for source evidence.
- Show retrieval progress states such as searching, reranking, and drafting grounded answer.
- Use refined hover, focus, and loading transitions.
- Keep motion subtle, premium, and performance-safe.

## Delivery workflow
Build the project in this order:
1. Define the pilot use case and representative query set.
2. Map sources, permissions, metadata, and update patterns.
3. Build ingestion and parsing pipeline.
4. Implement chunking, embeddings, indexing, and retrieval.
5. Add hybrid retrieval, metadata filters, and reranking.
6. Build grounded answer generation with citations.
7. Create premium animated frontend experience.
8. Add governance, logs, and evaluation harness.
9. Validate against real queries.
10. Add workflow integrations after trust and quality are proven.

## Output expectations
Generate:
- Product architecture
- Folder structure
- Frontend and backend modules
- Retrieval pipeline
- Database schema suggestions
- UI component hierarchy
- Motion system guidance
- Admin workflow design
- Evaluation strategy
- Phased roadmap

## Quality bar
The result must feel like a real enterprise AI product plan and implementation guide, not a hackathon prototype. Every major decision should support trust, retrieval quality, maintainability, premium UX, and staged deployment.

## Source documents
Use the following files as full context and requirements input:

--- FILE: rag_chatbot_prd.md ---
# Premium PRD: RAG Chatbot for Company Documents

## Product overview

This product is an internal AI assistant that answers questions over company documents using retrieval-augmented generation, with answers grounded in approved company sources rather than only the model's parametric memory [cite:18]. The production goal is not just a chat box over PDFs; it is a controlled knowledge layer that combines ingestion, retrieval, permissions, evaluation, and workflow integration so teams can trust answers in day-to-day work [cite:18].

The first release should focus on one narrow, high-value use case such as policy Q&A, onboarding knowledge, contract assistance, sales enablement, or internal support operations, because staged rollout reduces product risk and improves evaluation quality [cite:18]. For a document-heavy chatbot, a retrieval-first framework choice is sensible because RAG quality depends more on ingestion, chunking, and retrieval design than on interface polish alone [cite:18][cite:19].

## Problem statement

Teams lose time switching across PDFs, folders, drives, CRM notes, SOPs, and chat threads to assemble answers, which creates duplicated research and inconsistent responses across departments [cite:18]. A weak internal chatbot often fails because it uses shallow vector search, poor chunking, weak metadata, and no permission controls, which makes answers sound good without being reliable enough for production use [cite:18].

The product must solve three core issues: slow information retrieval, inconsistent answers, and poor operational handoff after answers are generated [cite:18]. The chatbot should therefore return grounded answers with citations, respect access scope before retrieval, and support follow-up workflow actions after an answer is produced [cite:18].

## Users and use cases

Primary users are internal knowledge workers such as HR, operations, legal, support, and sales staff who need fast answers from approved company documents [cite:18]. Typical questions include policy lookup, contract changes, invoice or client record checks, product or process clarification, onboarding help, and weekly operational summaries [cite:18].

The strongest early use cases are those where current knowledge changes often, because RAG is better than fine-tuning for runtime access to changing company information [cite:18]. High-value example flows include “What changed in the latest contract?”, “Which policy applies here?”, “What happened last week across operations?”, and “Which accounts are at payment risk?” [cite:18].

## Product goals

- Reduce time spent searching across internal knowledge sources by centralizing retrieval into one assistant experience [cite:18].
- Improve answer consistency with evidence-backed responses and visible source citations [cite:18].
- Enforce permission-aware retrieval so users only see content they are allowed to access [cite:18].
- Create a path from answer to action by integrating task creation, summaries, reporting, or CRM updates after the response [cite:18].
- Establish measurable quality through retrieval and answer evaluation before broader rollout [cite:18].

## Success metrics

A production RAG system should be measured across both retrieval quality and answer quality rather than by how “smart” the demo feels [cite:18]. The core metrics are context precision, context recall, answer faithfulness, answer relevance, citation quality, latency, and escalation behavior when the model should abstain or ask for clarification [cite:18].

Recommended launch targets for an internal MVP are: median answer latency under 6 seconds, citation presence in at least 95 percent of successful answers, a documented test set for representative queries, and manual evaluation showing high faithfulness on the pilot use case [cite:18]. Framework overhead is usually not the main runtime bottleneck because model latency dominates, so quality targets should prioritize retrieval correctness before micro-optimizing orchestration code [cite:19].

## Scope

### In scope for MVP

- Secure document ingestion for PDF, DOCX, TXT, HTML, and knowledge-base exports.
- Metadata extraction and tagging for source, owner, department, date, permission level, and version status [cite:18].
- Chunking that preserves section structure, parent-child context, and table integrity where possible [cite:18].
- Hybrid retrieval using dense retrieval plus keyword retrieval, metadata filters, and reranking [cite:18].
- Answer generation with citations and explicit uncertainty behavior [cite:18].
- Admin ingestion workflow and document refresh process.
- Internal web chat UI with premium, animated design system.
- Basic analytics, evaluation harness, and pilot feedback loop.

### Out of scope for MVP

- Full GraphRAG across multi-entity operational graphs unless the use case strongly depends on relationship traversal [cite:18].
- Open public chatbot access.
- Autonomous multi-step agents that can change business systems without approval.
- Multi-language support unless documents already require it in the pilot.

## Functional requirements

### Knowledge ingestion

The system must ingest documents from company-approved sources and preserve business context as metadata because retrieval control depends heavily on well-structured ingestion [cite:18]. Each stored chunk should retain links to the original document, version, section, source system, access level, and owner when available [cite:18].

### Retrieval

The system must support hybrid retrieval because semantic search alone can miss exact identifiers such as invoice numbers, product SKUs, contract clauses, and internal labels [cite:18]. Retrieval must combine dense vector search, sparse keyword retrieval, metadata filters, and a reranking stage before context is sent to the generation model [cite:18].

### Response generation

Responses must be grounded in retrieved evidence and present citations to underlying sources so users can verify claims [cite:18]. The assistant should decline or qualify answers when retrieved evidence is weak, conflicting, or outside the user’s access scope, since escalation behavior is a core production metric [cite:18].

### Permissions and governance

Access control must apply before generation, not after, because enterprise trust breaks when restricted data is surfaced in answers [cite:18]. Governance should include role-based access, source-level permissions, sensitivity labels, audit logs, version awareness, and refusal behavior for restricted content [cite:18].

### Workflow integration

The assistant should support post-answer actions such as opening a task, drafting a summary, creating a weekly report, or handing off a recommended next step to another system, because the highest business value often comes when answers move work forward rather than stopping at Q&A [cite:18].

## Non-functional requirements

- High trust: grounded answers, citations, permissions, auditability [cite:18].
- Reliability: document refreshes should not corrupt existing index integrity.
- Scalability: start with pilot corpus, but allow migration from local prototype tooling to production-grade vector infrastructure as document count and concurrency increase [cite:17][cite:20].
- Observability: log retrieval candidates, reranking outcomes, answer traces, and evaluation results [cite:19].
- Maintainability: modular ingestion and retrieval layers so framework choices can evolve.

## User experience requirements

The UI should feel premium, calm, and executive rather than like a generic AI template. A polished internal assistant needs a refined visual identity, subtle motion, clear hierarchy, and visible citations near answer blocks so trust is reinforced during use.

The answer view should emphasize four elements: the response, source citations, confidence or uncertainty cues, and recommended next actions. Empty states, loading states, and document sync states should be intentionally designed because product polish includes system states, not just the happy path.

## Risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Poor ingestion quality | Bad parsing and weak metadata lead to weak retrieval [cite:18]. | Build ingestion QA, metadata validation, and source-specific parsing. |
| Naive chunking | Mechanical splitting reduces retrieval quality even with strong embeddings [cite:18]. | Chunk by headings, clauses, sections, and preserve parent context. |
| Vector-only search | Exact identifiers may be missed [cite:18]. | Use hybrid retrieval plus reranking. |
| Overexposure of restricted data | Trust and compliance failure [cite:18]. | Enforce retrieval-time permissions and audit trails. |
| Premature complexity | Graph and agent layers can overcomplicate early product design [cite:18][cite:19]. | Start narrow with one strong use case and staged rollout. |
| Prototype stack in production | Local-first tools can bottleneck at scale [cite:17][cite:20]. | Prototype with Chroma, migrate to Weaviate or Pinecone when concurrency and corpus size grow [cite:17][cite:20]. |

## Release plan

### Phase 1: Discovery and data audit

Select one high-value use case, map source systems, define metadata fields, and document access rules before building the assistant, because staged implementation works best when data foundations are fixed early [cite:18]. Create a representative query set from real users so evaluation is built into the project from the beginning [cite:18].

### Phase 2: MVP retrieval layer

Implement ingestion, chunking, embeddings, hybrid retrieval, reranking, and grounded answer generation with citations [cite:18]. Use a document-oriented framework that is optimized for RAG-first development so the team can ship a strong retrieval baseline quickly [cite:19][cite:2].

### Phase 3: Premium UI and analytics

Build the animated internal chat interface, session traces, admin indexing view, and evaluation dashboards. Add human review workflows for failed or low-confidence answers.

### Phase 4: Workflow integration

After quality is proven, connect downstream actions such as task creation, CRM note drafting, ticket summaries, or operational reporting, since workflow-connected assistants create more value than standalone chat alone [cite:18].

## Acceptance criteria

- Users can ask document questions and receive grounded answers with visible citations.
- Retrieval respects role-based access and document-level restrictions [cite:18].
- Hybrid retrieval and reranking demonstrably outperform vector-only baseline on pilot questions [cite:18].
- Admins can reindex updated documents without full system failure.
- The interface supports premium motion, loading states, empty states, and source drill-down.
- A documented evaluation set exists and is used before pilot expansion [cite:18].

## Product positioning

This product should be framed as a secure internal knowledge assistant, not as a novelty chatbot. The most credible story is speed plus trust: faster answers, better citations, better access control, and better operational follow-through than manual search or a generic AI wrapper [cite:18].


--- FILE: rag_chatbot_tech_design.md ---
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


--- FILE: rag_chatbot_workflow.md ---
# Workflow Document: Building the Premium RAG Chatbot

## Workflow overview

The workflow should move from business problem definition to data preparation, retrieval quality, premium interface design, evaluation, and only then workflow automation, because mature RAG systems become reliable through staged implementation rather than direct full-scope builds [cite:18]. The core sequence is source ingestion, indexing, retrieval, generation, evaluation, and operational action [cite:18].

## End-to-end workflow

### 1. Use-case definition

Pick one high-value department use case and define the first query set from real users, because enterprise rollout works best when the initial problem is narrow and measurable [cite:18]. Example pilots include HR policy assistant, internal onboarding bot, support knowledge bot, or contract analysis assistant [cite:18].

### 2. Source mapping

List all document sources, source owners, update frequencies, permission rules, and metadata fields. This is critical because structured ingestion and source context drive retrieval quality later in the pipeline [cite:18].

### 3. Ingestion pipeline

Documents are uploaded or synced, parsed, normalized, de-duplicated, versioned, and tagged with metadata. Bad ingestion cannot be repaired later by prompting, so this stage should include validation and parsing QA [cite:18].

### 4. Chunking and indexing

Content is split by section structure, headings, clauses, tables, or threaded context depending on source type, then embedded and stored for retrieval [cite:18]. Parent-child relationships should be preserved so precise matches can still expand into broader context for answer generation [cite:18].

### 5. Retrieval pipeline

The query passes through access checks, hybrid retrieval, metadata filtering, merging, and reranking before answer generation [cite:18]. This stage exists because semantic-only search often misses exact identifiers and fast first-pass retrieval is not precise enough by itself [cite:18].

### 6. Answer generation

The model drafts an answer only from approved retrieved evidence, attaches citations, and expresses uncertainty when evidence is weak or insufficient [cite:18]. The UI should visibly separate answer text from evidence panels to reinforce trust.

### 7. Human review and evaluation

Evaluation must compare outputs against a real test set using context precision, context recall, faithfulness, answer relevance, citation quality, latency, and escalation behavior, because a non-evaluated RAG system is only a demo [cite:18]. Failed queries should be labeled by root cause such as parsing issue, chunking issue, search miss, reranking miss, or answer synthesis error.

### 8. Workflow integration

Only after retrieval quality is proven should the assistant write back to external systems or trigger downstream actions like task creation, reports, summaries, or CRM follow-ups [cite:18]. This ordering reduces risk and keeps automation aligned with trusted evidence [cite:18].

## Premium design workflow

The visual workflow for the product should run in parallel with technical development so the experience feels productized from the start rather than skinned at the end. The recommended sequence is design system, chat shell, citation UX, answer cards, admin analytics views, then interaction polish.

### Design phases

1. Brand direction: define tone as premium, calm, intelligent, and internal-enterprise.
2. Design system: color tokens, type tokens, spacing, elevation, and motion language.
3. Core screens: home, chat, source drawer, answer state, no-results state, admin indexing, analytics.
4. Motion pass: loading sequences, answer reveal, drawer transitions, hover states, system toasts.
5. Trust pass: permissions indicators, citations, source previews, restricted-content behavior.

## Delivery workflow by sprint

| Sprint | Focus | Deliverables |
|---|---|---|
| Sprint 1 | Product framing and data audit | Use case definition, source map, metadata schema, evaluation query set |
| Sprint 2 | Ingestion foundation | Parser selection, source connectors, chunking rules, indexing scripts |
| Sprint 3 | Retrieval baseline | Embeddings, vector store, keyword retrieval, metadata filters, reranker |
| Sprint 4 | Chat experience | Chat UI, answer cards, citations, source drawer, session flows |
| Sprint 5 | Evaluation and governance | Test harness, failure logging, role-based access, audit logs |
| Sprint 6 | Workflow actions | Task creation, summary drafting, reporting hooks, admin analytics |
| Sprint 7 | Polish and launch | Motion pass, performance tuning, pilot rollout, feedback loop |

## Team responsibilities

- Product owner: defines use cases, acceptance criteria, rollout scope.
- ML or AI engineer: ingestion, embeddings, retrieval tuning, evaluation.
- Backend engineer: APIs, auth, audit logs, source sync, workflow actions.
- Frontend engineer or product designer: premium animated interface, citation UX, dashboard polish.
- Domain reviewers: validate correctness on pilot questions.

## Approval gates

The project should not move into broad rollout until four gates are passed: pilot retrieval quality, permission correctness, answer faithfulness, and stakeholder trust in citations. These are the right gates because production RAG fails more often from shallow system design than from lack of raw model intelligence [cite:18].

