# 🌉 SETU — सेतु

**AI Bridge to Rights, Schemes & Opportunities**

> *SETU (सेतु = bridge) is a multi-agent AI system that helps low-literacy, rural, and first-generation Indian citizens discover and actually claim the government scholarships, welfare schemes, and livelihood opportunities they're eligible for — in their own language, with every claim traceable to a real source document.*

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![IBM Granite](https://img.shields.io/badge/LLM-IBM%20Granite%203.3-purple.svg)](https://www.ibm.com/granite)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Problem Statement

**268 million Indians live below the poverty line.** Many are eligible for government scholarships, pensions, and skill-training programs — but never apply because:

- They don't know which schemes exist
- They can't navigate complex eligibility criteria
- They speak Hindi or regional languages but forms are in English
- There's no single place that shows *all* schemes they qualify for
- Misinformation and fake scheme names are rampant

**SETU bridges this gap** with a trustworthy AI assistant that:
1. Understands the user's situation in their own language
2. Matches them with real, verified government schemes
3. Verifies every claim against official source documents
4. Creates an actionable step-by-step plan with required documents

---

## 🎯 SDG Alignment

| SDG | Goal | How SETU Contributes |
|-----|------|---------------------|
| **SDG 1** | No Poverty | Connects BPL families to welfare pensions, MGNREGA employment |
| **SDG 4** | Quality Education | Matches students with scholarships (SC/ST/OBC/Minority) |
| **SDG 8** | Decent Work | Links to PMKVY skill training, NCS job portal |
| **SDG 10** | Reduced Inequalities | Targets marginalized groups: SC, ST, OBC, MBC, minorities, widows, orphans |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit Chat UI                          │
│              (Hindi + English, Mobile-friendly)               │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────┐
│              LangGraph Orchestrator                           │
│         (Conditional routing based on intent)                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │  Language &  │───▶│ Eligibility  │───▶│  Verification   │  │
│  │   Intake     │    │  & Scheme    │    │  & Grounding    │  │
│  │   Agent      │    │   Agent      │    │    Agent        │  │
│  └─────────────┘    └──────────────┘    └─────────────────┘  │
│         │                                       │             │
│         │           ┌──────────────┐            │             │
│         └──────────▶│ Opportunity  │◀───────────┘             │
│                     │   Agent      │                          │
│                     └──────┬───────┘                          │
│                            │                                  │
│                     ┌──────▼───────┐                          │
│                     │  Planner &   │                          │
│                     │ Action Agent │                          │
│                     └──────────────┘                          │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  IBM Granite 3.3 8B (via Ollama)  │  ChromaDB Vector Store   │
│  Local inference, zero API cost   │  98 chunks, 18 schemes   │
└──────────────────────────────────────────────────────────────┘
```

### Agent Descriptions

| Agent | Role | Key Feature |
|-------|------|-------------|
| **Language & Intake** | Detects Hindi/English, extracts structured user profile | Handles Hinglish naturally |
| **Eligibility & Scheme** | RAG retrieval from ChromaDB → Granite synthesis | Never answers from parametric memory alone |
| **Verification & Grounding** | Deterministic confidence scoring | Real formula, not LLM self-assessment |
| **Opportunity** | Matches skill training & job opportunities | PMKVY + NCS portal integration |
| **Planner & Action** | Generates checklist, documents, draft messages | Simple language for low-literacy users |

### Verification Formula

```
confidence = 0.3 × citation_present + 0.3 × retrieval_similarity + 0.4 × claim_coverage
```

| Score | Verdict | Meaning |
|-------|---------|---------|
| ≥ 0.70 | ✅ VERIFIED | Claim well-grounded in source documents |
| 0.40–0.69 | ⚠️ NEEDS_REVIEW | Partially grounded, recommend manual confirmation |
| < 0.40 | ❌ UNVERIFIED | Cannot be confirmed from available sources |

---

## 🛠️ IBM Technology Used

| Technology | Usage |
|-----------|-------|
| **IBM Granite 3.3 8B** | Core LLM for all agents (intent extraction, RAG synthesis, plan generation) |
| **IBM watsonx Granite family** | Model architecture — open, enterprise-grade, multilingual |
| Served via **Ollama** | Local inference, zero API cost, runs on consumer hardware |

---

## 📊 Data Sources

**18 verified scheme documents** from official Indian government portals:

| Category | Count | Sources |
|----------|-------|---------|
| National Scholarships (SC/ST/OBC/Minority) | 6 | scholarships.gov.in, myscheme.gov.in |
| National Welfare (PM Kisan, MGNREGA, Widow Pension) | 4 | pmkisan.gov.in, nrega.nic.in, nsap.nic.in |
| Rajasthan State Schemes | 6 | sje.rajasthan.gov.in, hte.rajasthan.gov.in |
| Opportunity Sources (PMKVY, NCS) | 2 | skillindiadigital.gov.in, ncs.gov.in |

Every document carries: **source URL**, **retrieval date**, **official portal link**.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Ollama** ([install from ollama.com](https://ollama.com))
- ~5 GB disk space for the Granite model

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd "SETU AI"

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull IBM Granite model
ollama pull granite3.3:8b

# 5. Build the vector store (one-time)
python -m ingestion.chroma_store

# 6. Launch the app
streamlit run ui/app.py
```

Then open **http://localhost:8501** in your browser.

### Demo Script

Try these queries to see SETU in action:

1. **English — SC student**: *"I am an SC student from Rajasthan, family income 2 lakh. I passed 12th with 65%. What scholarships can I get?"*
2. **Hindi — widow pension**: *"मैं एक विधवा हूँ, BPL परिवार से हूँ, उम्र 50 साल है। मुझे कौन सी पेंशन मिल सकती है?"*
3. **Farmer query**: *"I am a farmer with 2 acres of land. What government help is available?"*
4. **Girl child savings**: *"My daughter is 4 years old. Is there any savings scheme for her?"*

---

## 📁 Project Structure

```
SETU AI/
├── agents/
│   ├── __init__.py
│   ├── language.py          # Language & Intake Agent
│   ├── eligibility.py       # RAG-grounded Eligibility Agent
│   ├── verification.py      # Verification & Grounding Agent
│   ├── opportunity.py       # Opportunity Agent
│   ├── planner.py           # Planner & Action Agent
│   └── orchestrator.py      # LangGraph Orchestrator
├── data/
│   ├── schemes/             # 16 verified scheme documents
│   └── opportunities/       # 2 opportunity source documents
├── ingestion/
│   ├── __init__.py
│   ├── docling_pipeline.py  # Document parser & chunker
│   └── chroma_store.py      # ChromaDB vector store
├── ui/
│   └── app.py               # Streamlit chat interface
├── tests/
│   └── test_self.py         # Self-test suite (6 diverse queries)
├── chroma_data/             # ChromaDB persistent storage
├── PROJECT_SPEC.md          # Original specification
├── PROGRESS.md              # Development progress log
├── TASKS.md                 # Phase checklist
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE (MIT)
└── README.md
```

---

## ⚠️ Limitations & What's Not Solved Yet

### Current Limitations
1. **Scheme count**: 18 schemes (16 welfare + 2 opportunity sources). Production system needs 500+.
2. **Geographic scope**: National schemes + Rajasthan state only. India has 28 states.
3. **No real-time updates**: Scheme data is static at ingestion time. Government schemes change frequently.
4. **No document upload**: Users can't upload their own certificates for automated eligibility checking.
5. **LLM hallucination risk**: Despite RAG + verification, the LLM may occasionally generate unsupported details. The verification agent flags these but can't prevent them entirely.
6. **Single-turn context**: Each query is independent; the system doesn't maintain multi-turn conversation context about the user's profile.
7. **Internet required**: Ollama runs locally but initial model download needs internet.

### What Would Break in Production
- **Scale**: ChromaDB is fine for 18 documents but would need a production vector DB (Pinecone, Weaviate) for 1000+ schemes.
- **Latency**: 5 sequential LLM calls take ~2-3 minutes on CPU. GPU or API-based inference would be needed.
- **Hindi quality**: Granite 3.3 8B handles Hindi adequately but larger models or fine-tuned models would be better.
- **Verification coverage**: Keyword-based fact coverage is a reasonable heuristic but not foolproof.

---

## 🔮 Future Sustainability

### Short-term (3-6 months)
- Add state-specific scheme data for all 28 states
- Implement WhatsApp bot interface (most accessible for rural users)
- Add periodic web scraping to keep scheme data current

### Medium-term (6-12 months)
- Partner with Common Service Centers (CSCs) for last-mile delivery
- Multi-turn conversation with persistent user profiles
- Document upload + OCR for automated eligibility verification
- Integration with DigiLocker for verified document access

### Long-term (1+ year)
- Voice interface in regional languages (speech-to-text + text-to-speech)
- Application status tracking via government API integration
- Community feedback loop: users report if scheme info was accurate
- Federation with state government portals for real-time data

---

## 🧪 Testing

Run the self-test suite:

```bash
python -m tests.test_self
```

This runs 6 diverse queries including:
- Normal scheme queries (English + Hindi)
- Low-confidence trigger (fabricated scheme name)
- Genuinely unanswerable query (out of scope)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **IBM Granite** — open-source LLM powering all agents
- **Government of India** — official scheme data from scholarships.gov.in, myscheme.gov.in, and state portals
- **LangChain / LangGraph** — agent orchestration framework
- **ChromaDB** — vector database for semantic search

---

<p align="center">
  <strong>SETU — सेतु — Building bridges to rights and opportunities</strong><br>
  <em>Built for IBM SkillsBuild AI Internship | SDG 1, 4, 8, 10</em>
</p>
