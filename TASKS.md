# SETU — Task Checklist

## Phase 0 — Setup & Real Data
- [x] Scaffold repo directories: /agents, /data/schemes, /data/opportunities, /ui, /ingestion, /tests
- [x] Create README.md, requirements.txt, .env.example, .gitignore, LICENSE
- [x] Pull IBM Granite 3.3 8B via Ollama
- [x] Collect 15–25 real scheme documents from official sources (18 collected)
- [x] Log collected files and source URLs in PROGRESS.md
- [x] **Checkpoint:** Show scraped file list to user for approval

## Phase 1 — Ingestion Pipeline
- [x] Build Docling/PDF pipeline -> structured, citable text chunks
- [x] Load chunks into ChromaDB with metadata (source URL, scheme name, retrieval date)
- [x] **Checkpoint:** Show one worked example of parsed, chunked, cited document

## Phase 2 — Eligibility + Verification Agents
- [x] Build RAG-grounded Eligibility agent
- [x] Build Verification agent with real grounding-score computation
- [x] Document the confidence formula and threshold
- [x] **Checkpoint:** Run one real query end-to-end, show citation + confidence score

## Phase 3 — Orchestrator + Opportunity + Planner Agents
- [x] Build LangGraph orchestrator with real conditional routing
- [x] Build Language & Intake agent
- [x] Build Opportunity agent
- [x] Build Planner & Action agent (checklist + draft message output)
- [x] **Checkpoint:** Full multi-agent trace visible in logs for one query

## Phase 4 — Chat Interface
- [x] Build Streamlit chat UI with Hindi + English support
- [x] Inject custom CSS: warm color palette, typography, mobile-friendly
- [x] Build visible agent trace side panel
- [x] **Checkpoint:** Working local demo, screenshot/recording saved

## Phase 5 — Self-Test & Fix
- [x] Run 5+ diverse realistic queries end-to-end
- [x] Include one low-confidence trigger query
- [x] Include one genuinely unanswerable query
- [x] Fix all bugs found; log in PROGRESS.md
- [x] **Checkpoint:** Written list of what broke and what was fixed

## Phase 6 — Repo Polish
- [x] README: problem statement, SDG mapping, architecture diagram, IBM tools, run instructions, demo script
- [x] README: "Limitations & what's not solved yet" section
- [x] README: Future sustainability paragraph
- [x] .gitignore for secrets, no API keys committed, LICENSE file
- [x] **Checkpoint:** Final review against Section 5 definition of done
