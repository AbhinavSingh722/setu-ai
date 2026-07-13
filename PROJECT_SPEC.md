# SETU — agentic AI bridge to rights, schemes & opportunities
## Master build prompt for Claude Opus 4.6 in Google Antigravity

You are the lead engineer building **Setu**, a multi-agent AI system that helps low-literacy, rural, and first-generation Indian citizens discover and actually claim the government scholarships, welfare schemes, and livelihood opportunities they're eligible for — in their own language, with every claim traceable to a real source document.

**Two success criteria, in this priority order:** (1) it must be genuinely correct and useful for a real person in this situation — never sacrifice accuracy or honesty for a better demo moment; (2) it is being submitted as a capstone/portfolio project for an IBM SkillsBuild–style AI internship selection, evaluated on technical execution, innovation, SDG/challenge fit, feasibility, and demonstrated use of IBM AI technology. Where the two conflict, (1) wins. Do not deviate from either without a strong reason logged in `PROGRESS.md`.

---

## Prerequisites — do this before opening Antigravity

1. Install Google Antigravity (antigravity.google) and sign in.
2. Install Ollama (ollama.com), then pull the current IBM Granite tag — check the exact tag name at ollama.com/library/granite first, since it changes as new Granite versions ship. A small "micro"/"mini"-class variant is enough here and keeps things fast on a laptop.
3. Confirm Python 3.10+ is installed.
4. Have a GitHub account ready — the finished repo needs to be public for submission.

Once these are done: open Antigravity, start a new workspace, select **Claude Opus 4.6** as the model, use **agent-assisted** mode (not full autopilot), and paste everything below as your first message.

## 0. Non-negotiable constraints — read before writing any code

- **Primary SDG:** 10 (Reduced Inequalities). Supporting: SDG 1 (No Poverty), SDG 4 (Quality Education), SDG 8 (Decent Work), SDG 16 (Strong Institutions).
- **Target users:** first-generation, rural/semi-urban students and informal-sector job seekers with low English/digital literacy — not general college students. This narrowness is deliberate; do not broaden it.
- **Geographic scope for the MVP:** national-level schemes + Rajasthan state schemes only. Do not attempt to cover all of India — a narrow, real, working demo beats a broad, fake one.
- **Tech stack (fixed, do not substitute without logging why in PROGRESS.md):**
  - LLM: IBM Granite (run locally via Ollama — free, no API key needed — or via watsonx.ai if the user supplies credentials). Never silently fall back to a different model family.
  - Document ingestion: Docling / Granite-Docling, to convert real scheme PDFs and notifications into structured, citable text chunks. Do not hand-type scheme data.
  - Agent orchestration: LangGraph (preferred, for explicit stateful multi-agent control) or Langflow. The orchestrator must be a real graph with conditional routing, not a fixed sequence of function calls.
  - Vector store: ChromaDB.
  - Interface: a single chat UI (Streamlit is fastest) that shows a visible **agent trace** — which agent is acting, what it retrieved, its confidence — not just a final answer.
  - Language: Python throughout.
- **Data honesty rule:** every scheme fact shown to a user must be traceable to a real, ingested source document. If the Eligibility agent cannot ground a claim, it must say so — never fabricate a scheme, deadline, or eligibility rule.
- **No paid dependency required for the core demo to run.** Granite via Ollama + open-source Docling/LangGraph/ChromaDB must work with zero API keys. Cloud/watsonx options are optional enhancements only.

---

## 1. Persistent memory files — create these FIRST, before any other code

Because this is a multi-session agentic build, context will get compacted or reset. These three files are your source of truth. **At the start of every session, read `PROGRESS.md` and `TASKS.md` before doing anything else — never try to reconstruct state from prior chat.**

1. **`PROJECT_SPEC.md`** — copy this entire prompt into it verbatim. This is the unabridged spec; refer back to it by section instead of re-deriving decisions.
2. **`PROGRESS.md`** — append a dated entry after every phase: what was built, what's left, any deviations from spec and why. Never delete old entries.
3. **`TASKS.md`** — the phase checklist below, copied in, checked off (`[x]`) as you complete each item.

---

## 2. Token-efficiency rules — follow these to avoid waste and drift

- Work **one phase at a time**, in order. Stop at each checkpoint marked below and summarize before continuing — do not run the whole build unsupervised in one pass.
- Do not re-read a file already in your active context unless you have reason to believe it changed.
- Prefer targeted diffs/edits over regenerating whole files.
- Do not re-explain architecture decisions already recorded in `PROJECT_SPEC.md` — reference the section number instead.
- If you're using Antigravity's Agent Manager, split independent phases (e.g. data ingestion vs. UI scaffolding) across parallel sub-agents rather than one sequential agent doing everything — but the Orchestrator/agent-logic phase (3) depends on ingestion (phase 1) being done first, so don't parallelize across that dependency.
- If context resets mid-phase, re-read `PROGRESS.md` + `TASKS.md`, not this whole prompt again.

---

## 3. The six agents (build exactly these — no more, no fewer)

| Agent | Job | Must NOT do |
|---|---|---|
| **Language & intake agent** | Normalizes Hindi/English/code-switched input into a structured intent + user situation | Guess missing facts — ask a follow-up instead |
| **Orchestrator agent** | Reads intent, decides which specialist agents to call and in what order, tracks conversation state, replans if a sub-agent fails or returns low confidence | Call every agent every time regardless of relevance |
| **Eligibility & scheme agent** | RAG over the Docling-ingested scheme corpus; returns candidate schemes with exact source citations | Answer from parametric memory without retrieval |
| **Verification & grounding agent** | Independently re-checks the Eligibility agent's claims against the retrieved source chunks; computes a real confidence score (e.g. citation presence + retrieval similarity threshold — not an LLM's self-reported guess); flags anything unverified | Pass through unverified claims silently |
| **Opportunity agent** | Surfaces relevant jobs, skilling programs, internships from a curated source set | Duplicate the Eligibility agent's scheme results |
| **Planner & action agent** | Turns verified results into a concrete checklist: required documents, deadline, and a draft message the user could send/forward | Just restate the recommendation in different words |

---

## 4. Build phases

### Phase 0 — Setup & real data (checkpoint: stop and show the user the scraped file list before continuing)
- Scaffold the repo: `/agents`, `/data/schemes`, `/data/opportunities`, `/ui`, `README.md`, `requirements.txt`, `.env.example`.
- Use your browser tool to collect 15–25 **real** scheme documents from official sources — do not fabricate any. Starting points to verify and browse (confirm these are current before relying on them):
  - National Scholarship Portal — scholarships.gov.in
  - MyScheme — myscheme.gov.in
  - PMKVY — pmkvyofficial.org
  - National Career Service — ncs.gov.in
  - Rajasthan state scholarship/welfare portal (search for the current official URL)
- Save raw PDFs/notifications into `/data/schemes`. Log exactly what was collected and its source URL in `PROGRESS.md`.

### Phase 1 — Ingestion pipeline (checkpoint: show one worked example of a parsed, chunked, cited document)
- Build the Docling pipeline that converts each source document into structured, citable chunks and loads them into ChromaDB with metadata (source URL, scheme name, retrieval date).

### Phase 2 — Eligibility + Verification agents (checkpoint: run one real query end-to-end and show the citation + confidence score)
- Build the RAG-grounded Eligibility agent.
- Build the Verification agent's real grounding-score computation. Define and document the exact formula/threshold used — this must be defensible if a judge asks "how is this computed."

### Phase 3 — Orchestrator + Opportunity + Planner agents (checkpoint: full multi-agent trace visible in logs for one query)
- Build the LangGraph orchestrator with real conditional routing (not a fixed pipeline).
- Build Opportunity and Planner agents. Planner output must include an actual checklist and draft message, not just a summary.

### Phase 4 — Chat interface (checkpoint: working local demo, screenshot/recording saved)
- Build this so it looks like a considered product, not a raw prototype — default unstyled Streamlit widgets read as unfinished, and that costs you on demo potential. Inject custom CSS: a warm, trustworthy color palette (not Streamlit's default gray/blue), clear typographic hierarchy, generous whitespace, and a mobile-friendly single-column layout — the real users of this system are far more likely to be on a phone than a laptop.
- Chat UI, Hindi + English, with a visible side panel or expandable trace showing which agent is acting and its confidence — this is the single most important thing for demo memorability, do not skip it.
- If time allows past this checkpoint, a custom FastAPI + HTML/CSS/JS frontend will look meaningfully more polished than styled Streamlit. Treat that as a stretch upgrade, not a requirement here — it must never block having a working demo.

### Phase 5 — Self-test & fix (checkpoint: a written list of what broke and what you fixed)
- Run at least 5 different realistic queries end to end, including one that should trigger a low-confidence flag and one the system genuinely can't answer well.
- Fix what breaks. Log every bug found and its fix in `PROGRESS.md` — a judge, and you, should trust a project more when its history shows real debugging, not one suspiciously clean pass.
- Do not skip this and jump straight to polish. A beautiful UI in front of a broken agent pipeline is worse than a plain UI in front of one that actually works.

### Phase 6 — Repo polish (checkpoint: final review against Section 5 before declaring done)
- `README.md` must include: problem statement, SDG mapping, architecture diagram (describe it in text/mermaid — a diagram already exists from this conversation, recreate its structure), IBM tools used and where, how to run locally with zero paid keys, and a 60–90 second demo script.
- `.gitignore` for secrets, no API keys committed, `LICENSE` file.

---

## 5. Definition of done — self-check against this before declaring finished

- [ ] A real Hindi or English query returns a cited, source-grounded answer end-to-end
- [ ] The Verification agent visibly flags at least one low-confidence case in the demo data (proves it isn't decorative)
- [ ] The agent trace is visible in the UI, not just the final answer
- [ ] Planner output includes a real checklist + draft message, not a restated summary
- [ ] README explicitly maps to SDG 10/1/4/8/16 and names every IBM technology used and why
- [ ] The whole thing runs with zero paid API keys (Granite via Ollama)
- [ ] At least 5 end-to-end test queries run and logged, with bugs and fixes documented in `PROGRESS.md`
- [ ] `PROGRESS.md` has a dated entry for every phase with no gaps

---

## 6. Beyond the demo — real-world honesty

Add a "Limitations & what's not solved yet" section to the README — a judge trusts a project more, not less, when it's explicit about what it doesn't do yet (schemes need periodic re-ingestion as deadlines change; no human-in-the-loop escalation is wired up yet; only Rajasthan + national schemes are covered). Add one paragraph on how this could realistically keep running after submission — a scheduled Docling re-ingestion job, and a handoff path to a real NGO or Common Service Centre for cases the Verification agent can't confidently resolve. This isn't decoration: an underserved user who gets confidently wrong information is worse off than one who gets an honest "I'm not sure, here's who to ask."

## 7. Demo script to include in the README

Open with a real voice/text query in Hindi from a first-generation rural student describing their situation. Show the orchestrator delegating live. Show the Eligibility agent's citations. Show the Verification agent flagging one claim as needing manual confirmation — this is the credibility moment, don't cut it for time. Close on the Planner agent's checklist and draft message. Total: under 90 seconds.
