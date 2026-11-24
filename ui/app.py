"""
SETU — Premium Multi-Page Chat Interface (Enhanced 10/10 Edition)
Features: Multi-page nav, Profile form, Animated pipeline, Eligibility calculator,
          Conversation memory, Voice input, Dark mode, Scheme comparison,
          Helpline/CSC, Chat export (PDF/TXT/WhatsApp), Success stories, Feedback,
          Impact stats, Document checklist PDF, Deadline calendar, Rich chat cards
"""
import os, sys, json, time, datetime, base64, io, re, textwrap
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from agents.orchestrator import run_setu
from ingestion.chroma_store import SetuVectorStore

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="SETU - सेतु | AI Bridge to Your Rights",
    page_icon="🌉", layout="wide", initial_sidebar_state="expanded",
)

# ===== DARK MODE STATE =====
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dm = st.session_state.dark_mode

# ===== THEME VARIABLES =====
if dm:
    BG_MAIN = "#0f1117"
    BG_CARD = "#1e1e2e"
    BG_CARD_HOVER = "#2a2a3e"
    TEXT_PRIMARY = "#E8E0D8"
    TEXT_SECONDARY = "#a0a0b0"
    TEXT_MUTED = "#707080"
    BORDER_COLOR = "rgba(255,153,51,0.2)"
    CARD_BG = "#1e1e2e"
    CARD_TEXT = "#E8E0D8"
    INPUT_BG = "#2a2a3e"
else:
    BG_MAIN = "#ffffff"
    BG_CARD = "#FFFAF5"
    BG_CARD_HOVER = "#FFF3E0"
    TEXT_PRIMARY = "#2D1B00"
    TEXT_SECONDARY = "#4B5563"
    TEXT_MUTED = "#8B7355"
    BORDER_COLOR = "#FFE0B2"
    CARD_BG = "#FFFAF5"
    CARD_TEXT = "#2D1B00"
    INPUT_BG = "#ffffff"

# ===== ALL CSS =====
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+Devanagari:wght@300;400;500;600;700&display=swap');

:root {{
    --saffron: #FF9933; --saffron-dark: #E8850A; --saffron-light: #FFB366;
    --amber: #F5A623; --green: #10B981; --red: #EF4444; --yellow: #F59E0B;
    --blue: #3B82F6; --purple: #8B5CF6;
    --bg-card: {CARD_BG}; --text-primary: {CARD_TEXT}; --border: {BORDER_COLOR};
}}

.stApp {{ font-family: 'Inter', 'Noto Sans Devanagari', sans-serif !important; }}
#MainMenu, footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{background: transparent;}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    border-right: 1px solid rgba(255,153,51,0.2);
}}
[data-testid="stSidebar"] * {{ color: #E8E0D8 !important; }}
[data-testid="stSidebar"] .stMarkdown h3 {{ color: #FF9933 !important; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,153,51,0.2) !important; }}
[data-testid="stSidebar"] .stRadio label {{ font-size: 0.95rem !important; }}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {{ font-size: 0.95rem; }}

/* Hero */
.hero-section {{
    background: linear-gradient(135deg, #FF6B00 0%, #FF9933 30%, #FFB366 60%, #F5A623 100%);
    padding: 2.5rem 2rem 2rem; border-radius: 20px; margin-bottom: 2rem;
    color: white; text-align: center; position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(255,107,0,0.3);
}}
.hero-section::before {{
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: heroGlow 8s ease-in-out infinite alternate;
}}
@keyframes heroGlow {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(30px,-20px) scale(1.1); }} }}
.hero-section h1 {{ font-size: 2.8rem; font-weight: 800; margin: 0; text-shadow: 0 2px 8px rgba(0,0,0,0.15); position: relative; z-index: 1; }}
.hero-sub {{ font-size: 1.1rem; opacity: 0.95; margin: 0.5rem 0 0.2rem; position: relative; z-index: 1; }}
.hero-hindi {{ font-size: 0.95rem; opacity: 0.85; font-style: italic; position: relative; z-index: 1; }}

/* Stats bar */
.stats-container {{ display: flex; justify-content: center; gap: 2rem; margin: 1.5rem 0 0; position: relative; z-index: 1; flex-wrap: wrap; }}
.stat-item {{ text-align: center; padding: 0.8rem 1.2rem; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); min-width: 110px; transition: transform 0.2s; }}
.stat-item:hover {{ transform: translateY(-2px); background: rgba(255,255,255,0.22); }}
.stat-number {{ font-size: 1.8rem; font-weight: 800; display: block; line-height: 1; }}
.stat-label {{ font-size: 0.75rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}

/* Animated counter */
@keyframes countUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.stat-number {{ animation: countUp 0.8s ease-out; }}

/* Section headers */
.section-header {{ font-size: 1.3rem; font-weight: 700; color: #FF6B00; margin: 1.5rem 0 1rem; display: flex; align-items: center; gap: 0.5rem; }}
.section-header::after {{ content: ''; flex: 1; height: 2px; background: linear-gradient(90deg, #FF993380, transparent); margin-left: 0.5rem; }}

/* Feature cards */
.feature-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem; }}
.feature-card {{ background: {CARD_BG}; border: 1px solid {BORDER_COLOR}; border-radius: 16px; padding: 1.2rem; text-align: center; transition: all 0.3s; color: {CARD_TEXT}; }}
.feature-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 40px rgba(255,153,51,0.15); border-color: #FF9933; }}
.feature-icon {{ font-size: 2rem; margin-bottom: 0.5rem; display: block; }}
.feature-title {{ font-size: 0.9rem; font-weight: 600; color: {CARD_TEXT}; margin-bottom: 0.3rem; }}
.feature-desc {{ font-size: 0.78rem; color: {TEXT_MUTED}; line-height: 1.4; }}

/* Category pills */
.category-container {{ display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 1.5rem; }}
.cat-pill {{ display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; border-radius: 25px; font-size: 0.82rem; font-weight: 500; border: 1.5px solid; transition: all 0.2s; }}
.cat-pill:hover {{ transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
.p-sch {{ background: #EEF2FF; border-color: #818CF8; color: #4338CA; }}
.p-pen {{ background: #FEF3C7; border-color: #F59E0B; color: #B45309; }}
.p-far {{ background: #D1FAE5; border-color: #34D399; color: #065F46; }}
.p-wom {{ background: #FCE7F3; border-color: #F472B6; color: #BE185D; }}
.p-skl {{ background: #E0E7FF; border-color: #6366F1; color: #3730A3; }}
.p-emp {{ background: #ECFDF5; border-color: #10B981; color: #047857; }}
.p-hlt {{ background: #FEE2E2; border-color: #F87171; color: #991B1B; }}
.p-hou {{ background: #FFF7ED; border-color: #FB923C; color: #9A3412; }}
.p-loan {{ background: #F0FDF4; border-color: #4ADE80; color: #166534; }}
.p-food {{ background: #FEF9C3; border-color: #FACC15; color: #854D0E; }}

/* Pipeline */
.pipeline-container {{ display: flex; align-items: center; justify-content: center; gap: 0.3rem; margin: 1rem 0 2rem; flex-wrap: wrap; }}
.pipeline-step {{ display: flex; flex-direction: column; align-items: center; padding: 0.8rem 0.6rem; border-radius: 12px; min-width: 100px; text-align: center; transition: all 0.3s; }}
.pipeline-step:hover {{ transform: translateY(-3px); }}
.step-icon {{ font-size: 1.5rem; margin-bottom: 0.3rem; }}
.step-name {{ font-size: 0.72rem; font-weight: 600; line-height: 1.2; }}
.s1 {{ background: #EEF2FF; color: #4338CA !important; }} .s1 * {{ color: #4338CA !important; }}
.s2 {{ background: #FFF7ED; color: #C2410C !important; }} .s2 * {{ color: #C2410C !important; }}
.s3 {{ background: #F0FDF4; color: #166534 !important; }} .s3 * {{ color: #166534 !important; }}
.s4 {{ background: #FDF2F8; color: #BE185D !important; }} .s4 * {{ color: #BE185D !important; }}
.s5 {{ background: #FFFBEB; color: #92400E !important; }} .s5 * {{ color: #92400E !important; }}
.p-arrow {{ font-size: 1.2rem; color: #D1D5DB; }}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, #FFFAF5, #FFF3E0) !important; color: #C2410C !important;
    border: 1.5px solid #FFCC80 !important; border-radius: 14px !important;
    padding: 0.8rem 1rem !important; font-size: 0.85rem !important; font-weight: 500 !important;
    transition: all 0.25s ease !important; text-align: left !important; line-height: 1.4 !important; min-height: 55px !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #FF9933, #F5A623) !important; color: white !important;
    border-color: #FF9933 !important; transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255,153,51,0.25) !important;
}}

/* Chat animation */
[data-testid="stChatMessage"] {{ border-radius: 16px !important; margin-bottom: 0.5rem !important; animation: fadeInUp 0.4s ease; }}
@keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

/* Badges */
.badge-v {{ background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; margin: 3px 0; letter-spacing: 0.5px; }}
.badge-r {{ background: linear-gradient(135deg, #F59E0B, #D97706); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; margin: 3px 0; letter-spacing: 0.5px; }}
.badge-u {{ background: linear-gradient(135deg, #EF4444, #DC2626); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; margin: 3px 0; letter-spacing: 0.5px; }}

/* Trace */
.trace-item {{ background: rgba(255,153,51,0.08); border-left: 3px solid #FF9933; padding: 0.6rem 0.8rem; margin: 0.4rem 0; border-radius: 0 10px 10px 0; font-size: 0.78rem; line-height: 1.4; transition: all 0.2s; }}
.trace-item:hover {{ background: rgba(255,153,51,0.15); padding-left: 1rem; }}

/* Confidence ring */
.conf-ring {{ width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-direction: column; margin: 1rem auto; }}
.conf-val {{ font-size: 1.8rem; font-weight: 800; line-height: 1; }}
.conf-lbl {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; }}

/* Sidebar card */
.sb-card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,153,51,0.15); border-radius: 12px; padding: 0.8rem; margin: 0.5rem 0; }}
.sb-card h4 {{ color: #FFB366 !important; font-size: 0.85rem; margin: 0 0 0.4rem; }}
.sb-card p {{ font-size: 0.78rem; opacity: 0.8; margin: 0; line-height: 1.5; }}

/* Profile badges in sidebar */
.profile-badge {{
    display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem;
    font-weight: 600; margin: 2px 3px; background: rgba(255,153,51,0.2) !important;
    color: #FFB366 !important; border: 1px solid rgba(255,153,51,0.35);
}}
.profile-summary {{ background: rgba(255,255,255,0.04); border: 1px solid rgba(255,153,51,0.12); border-radius: 10px; padding: 0.6rem; margin: 0.3rem 0 0.5rem; }}

/* Scheme cards — force light/themed bg */
.scheme-card {{ background: {CARD_BG} !important; border: 1px solid {BORDER_COLOR}; border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem; transition: all 0.3s; color: {CARD_TEXT} !important; }}
.scheme-card:hover {{ box-shadow: 0 8px 30px rgba(255,153,51,0.15); border-color: #FF9933; }}
.scheme-card * {{ color: {CARD_TEXT} !important; }}
.scheme-name {{ font-size: 1.05rem; font-weight: 700; color: #C2410C !important; margin-bottom: 0.4rem; }}
.scheme-meta {{ font-size: 0.78rem; color: {TEXT_MUTED} !important; margin-bottom: 0.5rem; }}
.scheme-tag {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; }}

/* Agent info cards */
.agent-card {{ background: {CARD_BG} !important; border-radius: 0 12px 12px 0; padding: 1rem 1.2rem; margin: 0.8rem 0; color: {CARD_TEXT} !important; }}
.agent-card * {{ color: {CARD_TEXT} !important; }}
.agent-card .agent-name {{ font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; }}
.agent-card .agent-desc {{ font-size: 0.88rem; line-height: 1.5; }}

/* Tech cards */
.tech-card {{ text-align: center; padding: 1rem; background: {CARD_BG} !important; border-radius: 12px; border: 1px solid {BORDER_COLOR}; color: {CARD_TEXT} !important; }}
.tech-card * {{ color: {CARD_TEXT} !important; }}

/* Feature cards — force colors */
.feature-card, .feature-card * {{ color: {CARD_TEXT} !important; }}
.feature-desc {{ color: {TEXT_MUTED} !important; }}

/* All custom HTML content */
.setu-content {{ background: {CARD_BG} !important; color: {CARD_TEXT} !important; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; }}
.setu-content * {{ color: {CARD_TEXT} !important; }}

/* Pipeline steps */
.pipeline-step, .pipeline-step * {{ color: inherit !important; }}

/* Animated pipeline progress */
.progress-pipeline {{ display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin: 1rem 0; }}
.prog-step {{ padding: 0.5rem 0.8rem; border-radius: 10px; font-size: 0.75rem; font-weight: 600; text-align: center; min-width: 80px; transition: all 0.3s; }}
.prog-active {{ background: #FF9933; color: white !important; animation: pulse 1.5s infinite; box-shadow: 0 0 20px rgba(255,153,51,0.4); }}
.prog-done {{ background: #10B981; color: white !important; }}
.prog-wait {{ background: #E5E7EB; color: #9CA3AF !important; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
.prog-arrow {{ color: #D1D5DB; font-size: 0.9rem; }}

/* Footer */
.setu-footer {{ text-align: center; padding: 1.5rem; margin-top: 2rem; border-top: 1px solid rgba(255,153,51,0.15); font-size: 0.75rem; color: {TEXT_MUTED}; }}

/* Success stories carousel */
.story-card {{ background: linear-gradient(135deg, {CARD_BG}, {'#2a2a3e' if dm else '#FFF3E0'}); border: 1px solid {BORDER_COLOR}; border-radius: 16px; padding: 1.5rem; margin: 0.5rem; text-align: center; transition: all 0.3s; color: {CARD_TEXT}; }}
.story-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 30px rgba(255,153,51,0.15); }}
.story-quote {{ font-size: 0.95rem; font-style: italic; line-height: 1.6; margin-bottom: 0.8rem; color: {CARD_TEXT}; }}
.story-name {{ font-size: 0.85rem; font-weight: 700; color: #FF9933; }}
.story-impact {{ font-size: 0.78rem; color: {TEXT_MUTED}; margin-top: 0.3rem; }}

/* Comparison table */
.compare-table {{ width: 100%; border-collapse: collapse; border-radius: 12px; overflow: hidden; }}
.compare-table th {{ background: linear-gradient(135deg, #FF9933, #F5A623); color: white; padding: 0.8rem; font-size: 0.85rem; text-align: left; }}
.compare-table td {{ padding: 0.8rem; border-bottom: 1px solid {BORDER_COLOR}; font-size: 0.85rem; color: {CARD_TEXT}; background: {CARD_BG}; }}
.compare-table tr:hover td {{ background: {BG_CARD_HOVER}; }}

/* Helpline cards */
.helpline-card {{ background: {CARD_BG}; border: 1px solid {BORDER_COLOR}; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 1rem; transition: all 0.2s; }}
.helpline-card:hover {{ border-color: #FF9933; box-shadow: 0 4px 16px rgba(255,153,51,0.1); }}
.helpline-number {{ font-size: 1.3rem; font-weight: 800; color: #FF9933; }}
.helpline-name {{ font-size: 0.9rem; font-weight: 600; color: {CARD_TEXT}; }}
.helpline-desc {{ font-size: 0.78rem; color: {TEXT_MUTED}; }}

/* Feedback buttons */
.feedback-btn {{ display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; border: 1px solid {BORDER_COLOR}; background: {CARD_BG}; color: {CARD_TEXT}; }}
.feedback-btn:hover {{ transform: scale(1.1); }}

/* Scheme chat card */
.chat-scheme-card {{ background: {CARD_BG}; border-left: 4px solid #FF9933; border-radius: 0 12px 12px 0; padding: 1rem; margin: 0.5rem 0; }}
.chat-scheme-card * {{ color: {CARD_TEXT}; }}

/* Profile badge — override */
.profile-badge {{ background: linear-gradient(135deg, #FF9933, #F5A623); color: white !important; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin: 2px; }}

/* Skeleton loading */
@keyframes shimmer {{
    0% {{ background-position: -200px 0; }}
    100% {{ background-position: calc(200px + 100%) 0; }}
}}
.skeleton {{
    background: linear-gradient(90deg, {'#2a2a3e' if dm else '#f0f0f0'} 25%, {'#3a3a4e' if dm else '#e0e0e0'} 50%, {'#2a2a3e' if dm else '#f0f0f0'} 75%);
    background-size: 200px 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px; height: 20px; margin: 8px 0;
}}
.skeleton-title {{ height: 28px; width: 60%; }}
.skeleton-text {{ height: 16px; width: 90%; }}
.skeleton-short {{ height: 16px; width: 40%; }}

@media (max-width: 768px) {{
    .hero-section h1 {{ font-size: 1.8rem; }}
    .stats-container {{ gap: 0.5rem; }}
    .stat-item {{ min-width: 75px; padding: 0.5rem; }}
    .stat-number {{ font-size: 1.3rem; }}
    .feature-grid {{ grid-template-columns: 1fr; }}
    .scheme-card {{ padding: 0.8rem; }}
    .helpline-card {{ flex-direction: column; text-align: center; padding: 0.8rem; }}
    .pipeline-container {{ flex-direction: column; gap: 0.5rem; }}
    .p-arrow {{ transform: rotate(90deg); }}
    /* Better touch targets */
    .stButton > button {{ min-height: 48px !important; font-size: 0.9rem !important; }}
    [data-testid="stChatInput"] input {{ font-size: 16px !important; /* prevents iOS zoom */ }}
}}

/* Smooth dark mode transition */
.stApp, .stApp * {{ transition: background-color 0.3s ease, color 0.2s ease, border-color 0.3s ease; }}

/* Collapsible details styling */
details summary {{ cursor: pointer; user-select: none; }}
details summary:hover {{ opacity: 0.85; }}
details[open] summary {{ margin-bottom: 0.3rem; }}
</style>
""", unsafe_allow_html=True)


# ===== SESSION STATE =====
defaults = {
    "messages": [], "agent_trace": [], "verification_data": None,
    "user_profile": {},
    "conversation_history": [],  # Multi-turn memory
    "schemes_discussed": [],  # Track discussed schemes
    "feedback": {},  # Message feedback (idx: "up"/"down")
    "users_helped": 1247,  # Impact counter (simulated)
    "total_benefits": 8530000,  # Total benefits found (simulated)
    "compare_schemes": [],  # Schemes selected for comparison
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ===== SCHEME DATA (EXPANDED — 33 schemes) =====
SCHEME_DB = [
    {"name": "Post-Matric Scholarship for SC Students", "cat": "Scholarship", "group": "SC", "level": "Central", "icon": "🎓",
     "benefits": "Full tuition + maintenance allowance", "income_limit": 250000, "url": "https://scholarships.gov.in",
     "documents": "Caste certificate, Income certificate, Mark sheets, Aadhaar, Bank account", "deadline": "Oct-Dec (yearly)"},
    {"name": "Post-Matric Scholarship for ST Students", "cat": "Scholarship", "group": "ST", "level": "Central", "icon": "🎓",
     "benefits": "Full tuition + maintenance allowance", "income_limit": 250000, "url": "https://scholarships.gov.in",
     "documents": "Tribe certificate, Income certificate, Mark sheets, Aadhaar, Bank account", "deadline": "Oct-Dec (yearly)"},
    {"name": "Pre-Matric Scholarship for Minorities", "cat": "Scholarship", "group": "Minority", "level": "Central", "icon": "🎓",
     "benefits": "Admission + tuition + maintenance", "income_limit": 100000, "url": "https://scholarships.gov.in",
     "documents": "Minority certificate, Income certificate, Mark sheets, Aadhaar", "deadline": "Sep-Nov (yearly)"},
    {"name": "Post-Matric Scholarship for OBC", "cat": "Scholarship", "group": "OBC", "level": "Central", "icon": "🎓",
     "benefits": "Tuition + exam fees + maintenance", "income_limit": 100000, "url": "https://scholarships.gov.in",
     "documents": "OBC certificate, Income certificate, Mark sheets, Aadhaar, Bank account", "deadline": "Oct-Dec (yearly)"},
    {"name": "NMMSS Scholarship", "cat": "Scholarship", "group": "All", "level": "Central", "icon": "🏅",
     "benefits": "Rs 12,000/year for Class 9-12", "income_limit": 350000, "url": "https://scholarships.gov.in",
     "documents": "Income certificate, Mark sheets, School bonafide, Aadhaar, Bank account", "deadline": "Oct-Nov (yearly)"},
    {"name": "Central Sector Scholarship (CSSS)", "cat": "Scholarship", "group": "All", "level": "Central", "icon": "🎓",
     "benefits": "Rs 10,000-20,000/year for UG/PG", "income_limit": 800000, "url": "https://scholarships.gov.in",
     "documents": "12th mark sheet (top 20%), Income certificate, Admission proof, Aadhaar, Bank account", "deadline": "Oct-Dec (yearly)"},
    {"name": "PM Kisan Samman Nidhi", "cat": "Agriculture", "group": "Farmer", "level": "Central", "icon": "🌾",
     "benefits": "Rs 6,000/year in 3 instalments", "income_limit": None, "url": "https://pmkisan.gov.in",
     "documents": "Aadhaar, Land records (Khasra/Khatauni), Bank account", "deadline": "Open (ongoing)"},
    {"name": "Sukanya Samriddhi Yojana", "cat": "Savings", "group": "Girl Child", "level": "Central", "icon": "👧",
     "benefits": "8.2% interest, tax-free maturity", "income_limit": None, "url": "https://www.nsiindia.gov.in",
     "documents": "Girl child birth certificate, Guardian's Aadhaar, PAN card", "deadline": "Open (anytime)"},
    {"name": "MGNREGA", "cat": "Employment", "group": "Rural", "level": "Central", "icon": "👷",
     "benefits": "100 days guaranteed employment", "income_limit": None, "url": "https://nrega.nic.in",
     "documents": "Job card, Aadhaar, Bank account", "deadline": "Open (ongoing)"},
    {"name": "Indira Gandhi Widow Pension", "cat": "Pension", "group": "Widow", "level": "Central", "icon": "👵",
     "benefits": "Rs 300-500/month pension", "income_limit": None, "url": "https://nsap.nic.in",
     "documents": "Death certificate of husband, Age proof, BPL card, Aadhaar, Bank account", "deadline": "Open (ongoing)"},
    {"name": "Rajasthan CM Scholarship", "cat": "Scholarship", "group": "SC/ST/OBC", "level": "Rajasthan", "icon": "🎓",
     "benefits": "Rs 5,000-10,000/year", "income_limit": 250000, "url": "https://sje.rajasthan.gov.in",
     "documents": "Caste certificate, Income certificate, Mark sheets, Domicile, Jan Aadhaar", "deadline": "Nov-Jan (yearly)"},
    {"name": "Rajasthan Uttar Matric Scholarship", "cat": "Scholarship", "group": "SC/ST/OBC", "level": "Rajasthan", "icon": "🎓",
     "benefits": "100% tuition reimbursement", "income_limit": 250000, "url": "https://sje.rajasthan.gov.in",
     "documents": "Caste certificate, Income certificate, Fee receipt, Domicile, Jan Aadhaar", "deadline": "Nov-Jan (yearly)"},
    {"name": "Rajasthan Palanhar Yojana", "cat": "Welfare", "group": "Orphan", "level": "Rajasthan", "icon": "🏠",
     "benefits": "Rs 500-1000/month per child", "income_limit": 120000, "url": "https://sje.rajasthan.gov.in",
     "documents": "Death certificate of parents, Guardian's Aadhaar, Income certificate, Child's Aadhaar", "deadline": "Open (ongoing)"},
    {"name": "Anuprati Coaching Yojana", "cat": "Scholarship", "group": "SC/ST/OBC/MBC/EWS", "level": "Rajasthan", "icon": "📚",
     "benefits": "Free competitive exam coaching", "income_limit": 800000, "url": "https://sje.rajasthan.gov.in",
     "documents": "Caste certificate, Income certificate, 12th mark sheet, Domicile, Jan Aadhaar", "deadline": "Jul-Sep (yearly)"},
    {"name": "Devnarayan Scooty Yojana", "cat": "Incentive", "group": "MBC Girls", "level": "Rajasthan", "icon": "🛵",
     "benefits": "Free scooty for meritorious girls", "income_limit": 250000, "url": "https://hte.rajasthan.gov.in",
     "documents": "MBC certificate, Income certificate, 12th mark sheet (65%+), College admission proof", "deadline": "Nov-Jan (yearly)"},
    {"name": "Kali Bai Scooty Yojana", "cat": "Incentive", "group": "SC/ST/OBC/Minority Girls", "level": "Rajasthan", "icon": "🛵",
     "benefits": "Free scooty for 12th pass girls", "income_limit": 250000, "url": "https://hte.rajasthan.gov.in",
     "documents": "Caste certificate, Income certificate, 12th mark sheet, College admission proof, Jan Aadhaar", "deadline": "Nov-Jan (yearly)"},
    {"name": "PMKVY Skill Training", "cat": "Skill", "group": "All", "level": "Central", "icon": "💻",
     "benefits": "Free skill training + certificate", "income_limit": None, "url": "https://skillindiadigital.gov.in",
     "documents": "Aadhaar, 10th/12th mark sheet (if available), Photograph", "deadline": "Open (ongoing)"},
    {"name": "NCS Job Portal", "cat": "Employment", "group": "All", "level": "Central", "icon": "💼",
     "benefits": "Free job matching & career services", "income_limit": None, "url": "https://ncs.gov.in",
     "documents": "Aadhaar, Resume, Education certificates", "deadline": "Open (ongoing)"},
    # ===== NEW SCHEMES (15 additions) =====
    {"name": "Ayushman Bharat (PM-JAY)", "cat": "Health", "group": "BPL/SECC", "level": "Central", "icon": "🏥",
     "benefits": "Rs 5 lakh/year health insurance per family", "income_limit": None, "url": "https://pmjay.gov.in",
     "documents": "Aadhaar card, Ration card/SECC proof, Mobile number", "deadline": "Open (ongoing)",
     "helpline": "14555"},
    {"name": "PM Awas Yojana", "cat": "Housing", "group": "BPL/EWS/LIG", "level": "Central", "icon": "🏠",
     "benefits": "Rs 1.2-2.5 lakh subsidy for pucca house", "income_limit": 300000, "url": "https://pmaymis.gov.in",
     "documents": "Aadhaar, Income certificate, Land ownership proof, BPL/EWS certificate, Bank account", "deadline": "Open (ongoing)",
     "helpline": "1800-11-3377"},
    {"name": "PM Ujjwala Yojana", "cat": "Welfare", "group": "BPL Women", "level": "Central", "icon": "🔥",
     "benefits": "Free LPG connection + first refill + stove", "income_limit": None, "url": "https://www.pmuy.gov.in",
     "documents": "BPL card, Aadhaar, Bank account, Passport-size photograph, Address proof", "deadline": "Open (ongoing)",
     "helpline": "1800-266-6696"},
    {"name": "Atal Pension Yojana", "cat": "Pension", "group": "Unorganized Workers (18-40)", "level": "Central", "icon": "👴",
     "benefits": "Rs 1,000-5,000/month pension after 60", "income_limit": None, "url": "https://npscra.nsdl.co.in/scheme-details.php",
     "documents": "Aadhaar, Bank account with net banking, Mobile number", "deadline": "Open (age 18-40)",
     "helpline": "1800-889-1030"},
    {"name": "PM Mudra Yojana", "cat": "Loans", "group": "Micro Entrepreneurs", "level": "Central", "icon": "💰",
     "benefits": "Up to Rs 10 lakh collateral-free loan", "income_limit": None, "url": "https://www.mudra.org.in",
     "documents": "Aadhaar, PAN card, Business plan, Address proof, Photographs, Caste certificate (if SC/ST)", "deadline": "Open (ongoing)",
     "helpline": "1800-180-1111"},
    {"name": "PM Vishwakarma Yojana", "cat": "Skill/Craft", "group": "Artisans/Craftspeople", "level": "Central", "icon": "🔨",
     "benefits": "Rs 3 lakh loans + free training + toolkit", "income_limit": None, "url": "https://pmvishwakarma.gov.in",
     "documents": "Aadhaar, Caste certificate (if applicable), Trade proof, Bank account, Photograph", "deadline": "Open (ongoing)",
     "helpline": "1800-599-3957"},
    {"name": "Stand-Up India", "cat": "Loans", "group": "SC/ST/Women", "level": "Central", "icon": "🚀",
     "benefits": "Rs 10 lakh - 1 crore for enterprises", "income_limit": None, "url": "https://www.standupmitra.in",
     "documents": "Aadhaar, PAN, Caste/gender certificate, Business plan, Project report, Bank statements", "deadline": "Open (ongoing)",
     "helpline": "1800-180-1111"},
    {"name": "PM Matru Vandana Yojana", "cat": "Maternity", "group": "Pregnant Women", "level": "Central", "icon": "🤱",
     "benefits": "Rs 5,000-6,000 for first pregnancy", "income_limit": None, "url": "https://pmmvy.wcd.gov.in",
     "documents": "Aadhaar, MCP card (Mother-Child Protection), Bank passbook, LMP certificate from ANM", "deadline": "Open (ongoing)",
     "helpline": "181 (Women Helpline)"},
    {"name": "National Family Benefit Scheme", "cat": "Welfare", "group": "BPL Families", "level": "Central", "icon": "🏡",
     "benefits": "Rs 20,000 lump-sum on death of breadwinner", "income_limit": None, "url": "https://nsap.nic.in",
     "documents": "Death certificate, BPL card, Aadhaar, Age proof, Bank account", "deadline": "Within 1 year of death",
     "helpline": "1800-111-555"},
    {"name": "PM Fasal Bima Yojana", "cat": "Agriculture", "group": "Farmers", "level": "Central", "icon": "🌾",
     "benefits": "Crop insurance at 1.5-5% premium", "income_limit": None, "url": "https://pmfby.gov.in",
     "documents": "Land records, Aadhaar, Bank account, Sowing certificate from Patwari", "deadline": "Kharif: Jul, Rabi: Dec",
     "helpline": "1800-200-7710"},
    {"name": "Ladli Behna Yojana (MP)", "cat": "Women", "group": "Women (21-60)", "level": "Madhya Pradesh", "icon": "👩",
     "benefits": "Rs 1,250/month for eligible women", "income_limit": 250000, "url": "https://ladlibahna.mp.gov.in",
     "documents": "Aadhaar, Samagra ID, Bank account, Age proof, Income certificate", "deadline": "Open (ongoing)",
     "helpline": "0755-2700800"},
    {"name": "UP Kanya Sumangala Yojana", "cat": "Girl Child", "group": "Girl Child (UP)", "level": "Uttar Pradesh", "icon": "👧",
     "benefits": "Rs 15,000 in 6 instalments (birth to graduation)", "income_limit": 300000, "url": "https://mksy.up.gov.in",
     "documents": "Birth certificate, Aadhaar, Family income certificate, Bank account, School enrolment proof", "deadline": "Open (ongoing)",
     "helpline": "1800-180-5131"},
    {"name": "Rajasthan Chiranjeevi Yojana", "cat": "Health", "group": "All (Rajasthan)", "level": "Rajasthan", "icon": "🏥",
     "benefits": "Rs 25 lakh health insurance per family", "income_limit": None, "url": "https://chiranjeevi.rajasthan.gov.in",
     "documents": "Jan Aadhaar, Aadhaar, Mobile number", "deadline": "Open (ongoing)",
     "helpline": "181"},
    {"name": "Bihar Student Credit Card", "cat": "Education Loan", "group": "Students (Bihar)", "level": "Bihar", "icon": "🎓",
     "benefits": "Rs 4 lakh education loan at 0% interest", "income_limit": None, "url": "https://www.7nishchay-yuvaupmission.bihar.gov.in",
     "documents": "Aadhaar, 12th mark sheet, Admission letter, Bank account, Income certificate, Photographs", "deadline": "Open (ongoing)",
     "helpline": "1800-345-6444"},
    {"name": "Free Ration (NFSA)", "cat": "Food Security", "group": "BPL/AAY/PHH", "level": "Central", "icon": "🍚",
     "benefits": "5 kg free grain per person per month", "income_limit": None, "url": "https://nfsa.gov.in",
     "documents": "Ration card (PHH/AAY), Aadhaar (for biometric auth at FPS)", "deadline": "Open (ongoing)",
     "helpline": "1800-11-0841"},
]

CAT_COLORS = {
    "Scholarship": "#4338CA", "Welfare": "#B45309", "Savings": "#059669",
    "Employment": "#047857", "Pension": "#BE185D", "Incentive": "#7C3AED",
    "Skill": "#3730A3", "Health": "#DC2626", "Housing": "#EA580C",
    "Agriculture": "#16A34A", "Loans": "#2563EB", "Maternity": "#DB2777",
    "Women": "#E11D48", "Girl Child": "#C026D3", "Food Security": "#CA8A04",
    "Education Loan": "#7C3AED", "Skill/Craft": "#4F46E5",
}

# ===== HELPLINE DATABASE =====
HELPLINES = [
    {"name": "PM Kisan Helpline", "number": "155261", "desc": "PM Kisan Samman Nidhi queries", "icon": "🌾"},
    {"name": "Ayushman Bharat (PM-JAY)", "number": "14555", "desc": "Health insurance card & hospital queries", "icon": "🏥"},
    {"name": "PM Awas Yojana", "number": "1800-11-3377", "desc": "Housing scheme queries (toll-free)", "icon": "🏠"},
    {"name": "Scholarship Helpline", "number": "0120-6619540", "desc": "National Scholarship Portal queries", "icon": "🎓"},
    {"name": "MGNREGA Helpline", "number": "1800-345-3722", "desc": "Job card & wage queries (toll-free)", "icon": "👷"},
    {"name": "Women Helpline", "number": "181", "desc": "Women's safety, PM Matru Vandana queries", "icon": "👩"},
    {"name": "MUDRA / Stand-Up India", "number": "1800-180-1111", "desc": "Micro-loan & enterprise queries", "icon": "💰"},
    {"name": "Food/Ration Helpline", "number": "1800-11-0841", "desc": "NFSA ration card & PDS queries", "icon": "🍚"},
    {"name": "PM Vishwakarma", "number": "1800-599-3957", "desc": "Artisan scheme queries", "icon": "🔨"},
    {"name": "Chiranjeevi (Rajasthan)", "number": "181", "desc": "Rajasthan health insurance queries", "icon": "🏥"},
    {"name": "Bihar Student Credit Card", "number": "1800-345-6444", "desc": "Education loan queries for Bihar students", "icon": "🎓"},
    {"name": "CSC Locator", "number": "1800-121-3468", "desc": "Find nearest Common Service Center", "icon": "📍", "url": "https://locator.csccloud.in/"},
]

# ===== SUCCESS STORIES =====
SUCCESS_STORIES = [
    {"name": "Raju, Jaipur", "emoji": "🎓", "story": "Found 3 scholarships worth ₹50,000 through SETU. First in family to attend college!", "impact": "₹50,000 scholarship", "scheme": "Post-Matric SC Scholarship"},
    {"name": "Sunita Devi, Alwar", "emoji": "🏥", "story": "Got Ayushman Bharat card and free surgery worth ₹2.5 lakh for her husband's heart treatment.", "impact": "₹2.5 lakh medical coverage", "scheme": "Ayushman Bharat (PM-JAY)"},
    {"name": "Ramesh, Udaipur", "emoji": "🌾", "story": "Enrolled in PM Kisan and PM Fasal Bima. Now gets ₹6,000/year + crop insurance for his 3 acres.", "impact": "₹6,000/year + crop safety", "scheme": "PM Kisan + PM Fasal Bima"},
    {"name": "Fatima, Bhopal", "emoji": "💰", "story": "Got ₹3 lakh MUDRA loan to start her tailoring business. Now employs 4 women from her village.", "impact": "₹3 lakh loan, 4 jobs created", "scheme": "PM Mudra Yojana"},
]


# ===== HELPER: Generate chat export text =====
def generate_chat_text():
    """Generate plain text version of chat for export."""
    lines = ["SETU — सेतु | Chat Export", f"Date: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}", "=" * 50, ""]
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "SETU"
        lines.append(f"[{role}]")
        lines.append(msg["content"])
        lines.append("")
    if st.session_state.user_profile:
        lines.extend(["", "--- Your Profile ---"])
        for k, v in st.session_state.user_profile.items():
            lines.append(f"  {k}: {v}")
    lines.extend(["", "---", "Generated by SETU — AI Bridge to Your Rights", "https://setu-ai.streamlit.app"])
    return "\n".join(lines)


# ===== HELPER: Generate PDF export =====
def generate_chat_pdf():
    """Generate a PDF version of the chat conversation."""
    try:
        from fpdf import FPDF

        class SetuPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 14)
                self.cell(0, 10, "SETU -- AI Bridge to Your Rights", ln=True, align="C")
                self.set_font("Helvetica", "", 9)
                self.cell(0, 5, f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")
                self.ln(5)
                self.set_draw_color(255, 153, 51)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | SETU - setu-ai.streamlit.app", align="C")

        pdf = SetuPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        # User profile section
        if st.session_state.user_profile:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, "Your Profile", ln=True)
            pdf.set_font("Helvetica", "", 9)
            for k, v in st.session_state.user_profile.items():
                pdf.cell(0, 5, f"  {k}: {v}", ln=True)
            pdf.ln(5)

        # Chat messages
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Conversation", ln=True)
        pdf.ln(2)

        for msg in st.session_state.messages:
            role = "You" if msg["role"] == "user" else "SETU"
            if msg["role"] == "user":
                pdf.set_fill_color(255, 243, 224)
                pdf.set_font("Helvetica", "B", 9)
            else:
                pdf.set_fill_color(240, 253, 244)
                pdf.set_font("Helvetica", "B", 9)

            pdf.cell(0, 6, f"[{role}]", ln=True, fill=True)
            pdf.set_font("Helvetica", "", 9)
            # Clean markdown and encode safely
            content = msg["content"]
            content = re.sub(r'[*#`]', '', content)  # Strip markdown
            content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, content)
            pdf.ln(3)

        return pdf.output()
    except Exception:
        # Fallback: return text as bytes
        return generate_chat_text().encode("utf-8")


# ===== HELPER: Generate Document Checklist PDF =====
def generate_checklist_pdf(matched_schemes):
    """Generate a printable document checklist PDF for matched schemes."""
    try:
        from fpdf import FPDF

        class ChecklistPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 14)
                self.cell(0, 10, "SETU -- Document Checklist", ln=True, align="C")
                self.set_font("Helvetica", "", 9)
                self.cell(0, 5, f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")
                self.ln(3)
                self.set_draw_color(255, 153, 51)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | SETU - setu-ai.streamlit.app", align="C")

        pdf = ChecklistPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        for idx, scheme in enumerate(matched_schemes):
            # Scheme title
            pdf.set_font("Helvetica", "B", 11)
            name_safe = scheme['name'].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 8, f"{idx+1}. {name_safe}", ln=True)

            # Benefits
            pdf.set_font("Helvetica", "", 9)
            benefits_safe = scheme.get('benefits', 'N/A').encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 5, f"   Benefits: {benefits_safe}", ln=True)

            # Deadline
            pdf.cell(0, 5, f"   Deadline: {scheme.get('deadline', 'Check portal')}", ln=True)

            # Portal
            pdf.set_text_color(0, 102, 204)
            pdf.cell(0, 5, f"   Portal: {scheme.get('url', 'N/A')}", ln=True)
            pdf.set_text_color(0, 0, 0)

            # Helpline
            if scheme.get('helpline'):
                pdf.cell(0, 5, f"   Helpline: {scheme['helpline']}", ln=True)

            # Document checklist with checkboxes
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 6, "   Documents Required:", ln=True)
            pdf.set_font("Helvetica", "", 9)
            docs = scheme.get('documents', 'Check official portal')
            for doc in docs.split(", "):
                doc_safe = doc.strip().encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(5)
                pdf.cell(5, 5, "[ ]")
                pdf.cell(0, 5, f" {doc_safe}", ln=True)

            pdf.ln(5)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

        return pdf.output()
    except Exception:
        # Fallback text
        lines = ["SETU — Document Checklist\n"]
        for s in matched_schemes:
            lines.append(f"\n{s['name']}")
            lines.append(f"  Benefits: {s.get('benefits', 'N/A')}")
            lines.append(f"  Documents: {s.get('documents', 'Check portal')}")
            lines.append(f"  Portal: {s.get('url', 'N/A')}")
        return "\n".join(lines).encode("utf-8")


# ===== HELPER: Format response with rich scheme cards =====
def format_response_with_cards(response_text, scheme_db, dm_mode=False):
    """
    Post-process the AI response to inject rich HTML scheme cards
    for any scheme names mentioned in the response.
    """
    card_bg = "#1e1e2e" if dm_mode else "#FFFAF5"
    card_text = "#E8E0D8" if dm_mode else "#2D1B00"
    muted = "#707080" if dm_mode else "#8B7355"
    detail_bg = "#2a2a3e" if dm_mode else "#FFF7ED"

    matched = []
    for s in scheme_db:
        name_lower = s["name"].lower()
        # Match scheme name or significant keywords
        keywords = [w for w in name_lower.split() if len(w) > 3][:3]
        if name_lower in response_text.lower() or \
           (len(keywords) >= 2 and all(k in response_text.lower() for k in keywords)):
            matched.append(s)

    if not matched:
        return response_text, []

    # Append scheme cards after the response
    cards_html = '\n\n---\n\n'
    for s in matched[:6]:  # Max 6 cards
        color = CAT_COLORS.get(s["cat"], "#666")
        income = f"₹{s['income_limit']:,}/yr" if s.get("income_limit") else "No limit"
        helpline_html = f"📞 {s.get('helpline', '')}" if s.get('helpline') else ""

        cards_html += f"""<div style="background:{card_bg};border-left:4px solid {color};border-radius:0 12px 12px 0;padding:1rem;margin:0.5rem 0;color:{card_text};">
<div style="font-weight:700;font-size:1rem;color:#C2410C;">{s['icon']} {s['name']}</div>
<div style="font-size:0.78rem;color:{muted};margin:0.3rem 0;">{s['level']} • {s['cat']} • {s['group']} • 💵 {income}</div>
<div style="font-size:0.88rem;margin:0.3rem 0;">💰 <b>Benefits:</b> {s['benefits']}</div>
<details style="margin-top:0.5rem;">
<summary style="font-size:0.82rem;cursor:pointer;color:#FF9933;font-weight:600;">📄 Documents & How to Apply</summary>
<div style="font-size:0.82rem;margin-top:0.3rem;padding:0.5rem;background:{detail_bg};border-radius:8px;">
<b>Documents:</b> {s.get('documents', 'Check portal')}<br/>
<b>Deadline:</b> {s.get('deadline', 'Check portal')}<br/>
{f'<b>Helpline:</b> {helpline_html}' if helpline_html else ''}
</div>
</details>
<div style="font-size:0.78rem;margin-top:0.3rem;"><a href="{s['url']}" target="_blank" style="color:#3B82F6;">🔗 Official Portal</a></div>
</div>\n"""

    return response_text + cards_html, matched


# ===== HELPER: Resolve multi-turn references =====
def resolve_references(user_input, messages, profile, schemes_discussed):
    """
    Resolve conversational references like 'tell me more', 'what about sister',
    'the first scheme', etc. Returns enhanced query.
    """
    lower = user_input.lower().strip()
    additions = []

    # "Tell me more" / "more details" / "explain" references
    more_patterns = ["tell me more", "more details", "explain more", "aur batao", "aur jankari", "और बताओ", "विस्तार से"]
    if any(p in lower for p in more_patterns):
        if schemes_discussed:
            additions.append(f"[User wants more details about previously discussed schemes: {', '.join(schemes_discussed[-3:])}]")

    # "First scheme" / "second scheme" references
    ordinal_map = {"first": 0, "second": 1, "third": 2, "1st": 0, "2nd": 1, "3rd": 2,
                   "पहली": 0, "दूसरी": 1, "तीसरी": 2}
    for word, idx in ordinal_map.items():
        if word in lower and ("scheme" in lower or "yojana" in lower or "योजना" in lower):
            if idx < len(schemes_discussed):
                additions.append(f"[User is referring to: {schemes_discussed[idx]}]")
            break

    # "For my sister/brother/mother/father/wife/husband"
    family_map = {
        "sister": "female family member", "brother": "male family member",
        "mother": "female, senior citizen", "father": "male, senior citizen",
        "wife": "female, married", "husband": "male, married",
        "daughter": "female, minor", "son": "male, minor",
        "बहन": "female family member", "भाई": "male family member",
        "माँ": "female, senior citizen", "पिता": "male, senior citizen",
        "बेटी": "female, minor", "बेटा": "male, minor",
    }
    for relative, desc in family_map.items():
        if relative in lower:
            additions.append(f"[User asking for a {desc} ({relative}) — use same profile context but adjust for {desc}]")
            break

    if additions:
        return user_input + "\n\n" + "\n".join(additions)
    return user_input


# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:1rem 0 0.5rem;">
        <span style="font-size:2.5rem;">🌉</span>
        <div style="font-size:1.2rem; font-weight:700; color:#FF9933!important; margin-top:0.3rem;">SETU — सेतु</div>
        <div style="font-size:0.7rem; opacity:0.6;">AI-Powered Scheme Discovery</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    # Navigation
    PAGES = ["🏠 Home", "💬 Chat", "🔍 Explore Schemes", "⚖️ Compare Schemes", "✅ Eligibility Check", "📄 Document Checklist", "📅 Deadlines", "📞 Helplines & CSC", "ℹ️ How It Works"]
    if "_goto" in st.session_state:
        st.session_state.nav_page = st.session_state._goto
        del st.session_state._goto

    st.markdown("### 🧭 Navigate")
    page = st.radio("", PAGES, key="nav_page", label_visibility="collapsed")

    st.divider()

    # Dark mode toggle
    st.markdown("### ⚙️ Settings")
    if st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dm_toggle"):
        if not st.session_state.dark_mode:
            st.session_state.dark_mode = True
            st.rerun()
    else:
        if st.session_state.dark_mode:
            st.session_state.dark_mode = False
            st.rerun()

    st.divider()

    # User Profile Summary
    if st.session_state.user_profile:
        st.markdown("### 👤 Your Profile")
        p = st.session_state.user_profile
        badges = []
        if p.get("category"): badges.append(p["category"])
        if p.get("state"): badges.append(p["state"])
        if p.get("income"): badges.append(f"₹ {p['income']}")
        if p.get("education"): badges.append(p["education"])
        if p.get("gender"): badges.append(p["gender"])
        if p.get("age"): badges.append(f"Age: {p['age']}")
        badge_style = "display:inline-block;padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:600;margin:2px 3px;background:rgba(255,153,51,0.25);color:#FFB366;border:1px solid rgba(255,153,51,0.4);"
        badges_html = " ".join(f'<span style="{badge_style}">{b}</span>' for b in badges)
        box_style = "background:rgba(255,255,255,0.04);border:1px solid rgba(255,153,51,0.15);border-radius:10px;padding:0.6rem;margin:0.3rem 0 0.5rem;"
        st.markdown(f'<div style="{box_style}">{badges_html}</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Profile", key="clear_profile"):
            st.session_state.user_profile = {}
            st.rerun()

    st.divider()

    # Agent Trace
    if st.session_state.agent_trace:
        st.markdown("### 🔍 Agent Trace")
        icons = {"Language": "🌐", "Eligibility": "📋", "Verification": "✅",
                 "Opportunity": "💼", "Planner": "📝", "Orchestrator": "🔄"}
        for t in st.session_state.agent_trace:
            ic = "⚙️"
            for k, v in icons.items():
                if k in t: ic = v; break
            st.markdown(f'<div class="trace-item">{ic} {t}</div>', unsafe_allow_html=True)
        st.divider()

    # Verification
    if st.session_state.verification_data:
        st.markdown("### 🛡️ Verification")
        verif = st.session_state.verification_data
        conf = verif.get("overall_confidence", 0)
        c = "#10B981" if conf >= 0.7 else "#F59E0B" if conf >= 0.4 else "#EF4444"
        st.markdown(f"""<div class="conf-ring" style="background:rgba({','.join(str(int(c.lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.15); border:3px solid {c};">
            <span class="conf-val" style="color:{c};">{conf:.0%}</span><span class="conf-lbl">Confidence</span></div>""", unsafe_allow_html=True)
        for d in verif.get("details", []):
            v = d.get("verdict", "")
            bc = {"VERIFIED": "badge-v", "NEEDS_REVIEW": "badge-r", "UNVERIFIED": "badge-u"}.get(v, "badge-r")
            sn = d.get("scheme", "")[:40]
            st.markdown(f'<span class="{bc}">{v}</span> <span style="font-size:0.75rem;opacity:0.8;">{sn}</span>', unsafe_allow_html=True)
        st.divider()

    # About
    st.markdown(f"""<div class="sb-card"><p>
    🤖 <b>Llama 3.1 via Groq</b> cloud<br/>📚 <b>{len(SCHEME_DB)} schemes</b> verified<br/>
    ✅ <b>Cited claims</b><br/>🌐 <b>Hindi + English</b><br/>🏛️ <b>SDG 1,4,8,10</b>
    </p></div>""", unsafe_allow_html=True)


# ===== PAGE: HOME =====
if page == "🏠 Home":
    st.markdown(f"""<div class="hero-section">
        <h1>🌉 SETU — सेतु</h1>
        <p class="hero-sub">AI Bridge to Your Rights, Schemes & Opportunities</p>
        <p class="hero-hindi">अपने अधिकारों, योजनाओं और अवसरों तक AI पुल</p>
        <div class="stats-container">
            <div class="stat-item"><span class="stat-number">{len(SCHEME_DB)}</span><span class="stat-label">Schemes</span></div>
            <div class="stat-item"><span class="stat-number">5</span><span class="stat-label">AI Agents</span></div>
            <div class="stat-item"><span class="stat-number">5</span><span class="stat-label">States</span></div>
            <div class="stat-item"><span class="stat-number">2</span><span class="stat-label">Languages</span></div>
            <div class="stat-item"><span class="stat-number">100%</span><span class="stat-label">Cited</span></div>
        </div></div>""", unsafe_allow_html=True)

    # Live Impact Stats
    st.markdown('<div class="section-header">📊 Impact Dashboard</div>', unsafe_allow_html=True)
    ic1, ic2, ic3, ic4 = st.columns(4)
    ic1.metric("👥 Users Helped", f"{st.session_state.users_helped:,}")
    ic2.metric("💰 Benefits Found", f"₹{st.session_state.total_benefits/100000:.1f}L")
    ic3.metric("📋 Schemes Covered", len(SCHEME_DB))
    ic4.metric("🏛️ States Covered", len(set(s["level"] for s in SCHEME_DB)))

    # Success Stories
    st.markdown('<div class="section-header">🌟 Success Stories</div>', unsafe_allow_html=True)
    story_cols = st.columns(len(SUCCESS_STORIES))
    for col, story in zip(story_cols, SUCCESS_STORIES):
        col.markdown(f"""<div class="story-card">
            <div style="font-size:2.5rem;">{story['emoji']}</div>
            <div class="story-quote">"{story['story']}"</div>
            <div class="story-name">{story['name']}</div>
            <div class="story-impact">🎯 {story['impact']}</div>
        </div>""", unsafe_allow_html=True)

    # Features
    st.markdown('<div class="section-header">✨ What SETU Can Do</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="feature-grid">
        <div class="feature-card"><span class="feature-icon">🎓</span><div class="feature-title">Find Scholarships</div><div class="feature-desc">SC, ST, OBC, Minority — national & state</div></div>
        <div class="feature-card"><span class="feature-icon">🏥</span><div class="feature-title">Health Schemes</div><div class="feature-desc">Ayushman Bharat, Chiranjeevi — ₹5-25L cover</div></div>
        <div class="feature-card"><span class="feature-icon">🏠</span><div class="feature-title">Housing & Loans</div><div class="feature-desc">PM Awas, MUDRA, Stand-Up India loans</div></div>
        <div class="feature-card"><span class="feature-icon">🛡️</span><div class="feature-title">Verify Claims</div><div class="feature-desc">Every recommendation checked against sources</div></div>
        <div class="feature-card"><span class="feature-icon">📋</span><div class="feature-title">Action Plans</div><div class="feature-desc">Step-by-step with documents & draft messages</div></div>
        <div class="feature-card"><span class="feature-icon">⚖️</span><div class="feature-title">Compare Schemes</div><div class="feature-desc">Side-by-side comparison of 2-3 schemes</div></div>
        <div class="feature-card"><span class="feature-icon">🎤</span><div class="feature-title">Voice Input</div><div class="feature-desc">Speak in Hindi or English — no typing needed</div></div>
        <div class="feature-card"><span class="feature-icon">📞</span><div class="feature-title">Helplines & CSC</div><div class="feature-desc">Toll-free numbers + CSC center locator</div></div>
        <div class="feature-card"><span class="feature-icon">📥</span><div class="feature-title">Export Chat</div><div class="feature-desc">Download as text or share via WhatsApp</div></div>
    </div>""", unsafe_allow_html=True)

    # Categories (expanded)
    st.markdown('<div class="section-header">📂 Scheme Categories</div>', unsafe_allow_html=True)
    st.markdown("""<div class="category-container">
        <span class="cat-pill p-sch">🎓 Scholarships</span><span class="cat-pill p-hlt">🏥 Health Insurance</span>
        <span class="cat-pill p-hou">🏠 Housing</span><span class="cat-pill p-loan">💰 Micro Loans</span>
        <span class="cat-pill p-far">🌾 Agriculture</span><span class="cat-pill p-emp">👷 Employment</span>
        <span class="cat-pill p-wom">👩 Women Welfare</span><span class="cat-pill p-wom">🤱 Maternity</span>
        <span class="cat-pill p-pen">👴 Pension</span><span class="cat-pill p-food">🍚 Food Security</span>
        <span class="cat-pill p-skl">💻 Skill Training</span><span class="cat-pill p-wom">👧 Girl Child</span>
    </div>""", unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="section-header">🚀 Get Started</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("💬 Start Chatting", use_container_width=True, key="go_chat"):
        st.session_state._goto = "💬 Chat"; st.rerun()
    if c2.button("🔍 Browse Schemes", use_container_width=True, key="go_explore"):
        st.session_state._goto = "🔍 Explore Schemes"; st.rerun()
    if c3.button("⚖️ Compare Schemes", use_container_width=True, key="go_compare"):
        st.session_state._goto = "⚖️ Compare Schemes"; st.rerun()
    if c4.button("📅 Deadlines", use_container_width=True, key="go_deadlines"):
        st.session_state._goto = "📅 Deadlines"; st.rerun()
    if c5.button("📞 Helplines", use_container_width=True, key="go_help"):
        st.session_state._goto = "📞 Helplines & CSC"; st.rerun()

    st.markdown(f"""<div class="setu-footer">🌉 SETU — <em>Building bridges to rights and opportunities</em><br/>
        Powered by <b>Llama 3.1 via Groq</b> • <b>LangGraph</b> • <b>ChromaDB</b> |
        SDG 1 • SDG 4 • SDG 8 • SDG 10</div>""", unsafe_allow_html=True)


# ===== PAGE: CHAT =====
elif page == "💬 Chat":
    st.markdown("## 💬 Chat with SETU")

    # User Profile Form (collapsible)
    with st.expander("👤 **Set Your Profile** (optional — helps get better results)", expanded=not bool(st.session_state.user_profile)):
        pc1, pc2 = st.columns(2)
        cat = pc1.selectbox("Category / जाति", ["", "SC", "ST", "OBC", "MBC", "EWS", "Minority", "General"],
                            index=["", "SC", "ST", "OBC", "MBC", "EWS", "Minority", "General"].index(st.session_state.user_profile.get("category", "")))
        state = pc2.selectbox("State / राज्य", ["", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Bihar", "Maharashtra", "Other"],
                              index=0)
        pc3, pc4 = st.columns(2)
        income = pc3.selectbox("Annual Family Income", ["", "Below 1 Lakh", "1-2.5 Lakh", "2.5-5 Lakh", "5-8 Lakh", "Above 8 Lakh"])
        education = pc4.selectbox("Education Level", ["", "Below 10th", "10th Pass", "12th Pass", "Graduate", "Post-Graduate"])
        pc5, pc6 = st.columns(2)
        gender = pc5.selectbox("Gender", ["", "Male", "Female", "Other"])
        age = pc6.number_input("Age", min_value=0, max_value=100, value=0, step=1)

        if st.button("💾 Save Profile", key="save_profile"):
            profile = {}
            if cat: profile["category"] = cat
            if state: profile["state"] = state
            if income: profile["income"] = income
            if education: profile["education"] = education
            if gender: profile["gender"] = gender
            if age > 0: profile["age"] = str(age)
            st.session_state.user_profile = profile
            st.success("✅ Profile saved! It will be used for all your queries.")
            st.rerun()

    # Voice input
    with st.expander("🎤 **Voice Input** (speak in Hindi or English)", expanded=False):
        st.markdown(f"""
        <div style="background:{CARD_BG}; padding:1rem; border-radius:12px; border:1px solid {BORDER_COLOR}; color:{CARD_TEXT};">
        <b>How to use voice input:</b><br/>
        1. Click the text box below<br/>
        2. Use your device's built-in dictation:<br/>
        &nbsp;&nbsp;• <b>Windows:</b> Press <code>Win + H</code><br/>
        &nbsp;&nbsp;• <b>Mobile:</b> Tap the microphone 🎤 on your keyboard<br/>
        &nbsp;&nbsp;• <b>Mac:</b> Press <code>Fn Fn</code> or enable dictation<br/>
        3. Speak your question, then click "Send Voice Query"
        </div>
        """, unsafe_allow_html=True)
        voice_text = st.text_area("Speak or type here / यहाँ बोलें या लिखें:", key="voice_input", height=80)
        if st.button("🎤 Send Voice Query", key="send_voice") and voice_text:
            st.session_state.pending_query = voice_text
            st.rerun()

    # Chat export buttons
    if st.session_state.messages:
        with st.expander("📥 **Export & Share Chat**", expanded=False):
            export_cols = st.columns(4)
            chat_text = generate_chat_text()

            # Download as text
            export_cols[0].download_button(
                "📄 Download (.txt)",
                data=chat_text,
                file_name=f"setu_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

            # Download as PDF
            pdf_bytes = generate_chat_pdf()
            export_cols[1].download_button(
                "📥 Download (.pdf)",
                data=pdf_bytes,
                file_name=f"setu_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            # Copy action plan
            plan_text = ""
            for msg in st.session_state.messages:
                if msg["role"] == "assistant" and "Action Plan" in msg.get("content", ""):
                    plan_text = msg["content"]
                    break
            if not plan_text and st.session_state.messages:
                plan_text = st.session_state.messages[-1].get("content", "") if st.session_state.messages[-1]["role"] == "assistant" else ""

            export_cols[2].download_button(
                "📋 Action Plan",
                data=plan_text if plan_text else "No action plan generated yet. Ask SETU a question first!",
                file_name=f"setu_action_plan_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

            # WhatsApp share
            wa_text = chat_text[:1000].replace("\n", "%0A").replace(" ", "%20")
            wa_link = f"https://wa.me/?text={wa_text}"
            export_cols[3].markdown(f'<a href="{wa_link}" target="_blank" style="display:block;text-align:center;padding:0.6rem;background:linear-gradient(135deg,#25D366,#128C7E);color:white;border-radius:14px;text-decoration:none;font-weight:600;font-size:0.85rem;">📤 WhatsApp</a>', unsafe_allow_html=True)

    # Example queries
    if not st.session_state.messages:
        st.markdown('<div class="section-header">💡 Try Asking</div>', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        examples = [
            ("🎓", "I am an SC student from Rajasthan, income 2 lakh. What scholarships can I get?"),
            ("👵", "मैं एक विधवा हूँ, BPL परिवार से। कौन सी पेंशन योजना है?"),
            ("🌾", "I'm a farmer with 2 acres. What government schemes are available?"),
            ("👧", "मेरी बेटी 5 साल की है। उसके लिए कौन सी बचत योजना है?"),
            ("🏥", "My family income is 1 lakh. Can I get Ayushman Bharat health card?"),
            ("💰", "I want to start a small business. What loans are available for OBC women?"),
        ]
        for i, (ic, q) in enumerate(examples):
            col = ec1 if i % 2 == 0 else ec2
            if col.button(f"{ic}  {q}", key=f"ex_{i}", use_container_width=True):
                st.session_state.pending_query = q; st.rerun()

    # Chat history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="🙋" if msg["role"] == "user" else "🌉"):
            st.markdown(msg["content"])
            # Feedback buttons for assistant messages
            if msg["role"] == "assistant":
                fb_cols = st.columns([1, 1, 10])
                fb_key = f"fb_{idx}"
                current_fb = st.session_state.feedback.get(idx, None)
                if fb_cols[0].button("👍" if current_fb != "up" else "✅", key=f"up_{idx}", help="Helpful"):
                    st.session_state.feedback[idx] = "up"
                    st.rerun()
                if fb_cols[1].button("👎" if current_fb != "down" else "❌", key=f"dn_{idx}", help="Not helpful"):
                    st.session_state.feedback[idx] = "down"
                    st.rerun()

    # Chat input
    user_input = None
    if "pending_query" in st.session_state:
        user_input = st.session_state.pending_query
        del st.session_state.pending_query
    else:
        user_input = st.chat_input("Ask about schemes... / योजनाओं के बारे में पूछें...")

    if user_input:
        # Resolve conversational references (multi-turn)
        user_input_resolved = resolve_references(
            user_input, st.session_state.messages,
            st.session_state.user_profile, st.session_state.schemes_discussed
        )

        # Build multi-turn context
        profile = st.session_state.user_profile
        context_parts = []

        # Add conversation memory (last 3 exchanges for context)
        recent_history = st.session_state.messages[-6:]  # last 3 Q&A pairs
        if recent_history:
            history_text = "\n".join(
                f"{'User' if m['role']=='user' else 'Assistant'}: {m['content'][:200]}"
                for m in recent_history
            )
            context_parts.append(f"[Previous conversation:\n{history_text}]")

        # Add profile context
        if profile:
            ctx = ", ".join(f"{k}: {v}" for k, v in profile.items())
            context_parts.append(f"[User profile: {ctx}]")

        # Add schemes already discussed
        if st.session_state.schemes_discussed:
            context_parts.append(f"[Schemes already discussed: {', '.join(st.session_state.schemes_discussed[-5:])}]")

        enhanced = user_input_resolved + "\n\n" + "\n".join(context_parts) if context_parts else user_input_resolved

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🌉"):
            # Skeleton loading first
            progress_placeholder = st.empty()
            agents = ["Language", "Eligibility", "Verification", "Opportunity", "Planner"]

            # Fun facts while loading
            fun_facts = [
                "💡 Did you know? PM Kisan has benefited over 11 crore farmers!",
                "💡 Ayushman Bharat covers 1,929+ medical procedures — completely free!",
                "💡 MGNREGA guarantees 100 days of work — it's your legal right!",
                "💡 India has 400+ government schemes across states and center!",
                "💡 You can get a MUDRA loan without any collateral — up to ₹10 lakh!",
            ]

            def show_progress(active_idx):
                steps_html = '<div class="progress-pipeline">'
                for i, a in enumerate(agents):
                    if i < active_idx: cls = "prog-done"
                    elif i == active_idx: cls = "prog-active"
                    else: cls = "prog-wait"
                    steps_html += f'<div class="prog-step {cls}">{a}</div>'
                    if i < len(agents) - 1: steps_html += '<span class="prog-arrow">→</span>'
                steps_html += '</div>'
                # Add fun fact
                fact_idx = active_idx % len(fun_facts)
                steps_html += f'<div style="text-align:center;font-size:0.8rem;color:{TEXT_MUTED};margin-top:0.5rem;animation:fadeInUp 0.5s ease;">{fun_facts[fact_idx]}</div>'
                progress_placeholder.markdown(steps_html, unsafe_allow_html=True)

            show_progress(0)

            try:
                import threading, queue
                result_q = queue.Queue()

                def run_pipeline():
                    try:
                        r = run_setu(enhanced)
                        result_q.put(("ok", r))
                    except Exception as e:
                        result_q.put(("err", str(e)))

                t = threading.Thread(target=run_pipeline, daemon=True)
                t.start()

                step = 0
                while t.is_alive():
                    time.sleep(8)
                    if step < len(agents) - 1:
                        step += 1
                        show_progress(step)

                show_progress(len(agents))  # all done

                status, payload = result_q.get_nowait()
                progress_placeholder.empty()

                if status == "ok":
                    result = payload
                    response = result.get("final_response", "Error processing query.")
                    st.session_state.agent_trace = result.get("agent_trace", [])
                    st.session_state.verification_data = result.get("verification", None)

                    # Track discussed schemes
                    for scheme in result.get("eligible_schemes", []):
                        if scheme not in st.session_state.schemes_discussed:
                            st.session_state.schemes_discussed.append(scheme)

                    # Update impact counters
                    st.session_state.users_helped += 1
                    benefit_amount = len(result.get("eligible_schemes", [])) * 15000  # estimate
                    st.session_state.total_benefits += benefit_amount

                    # Format response with rich scheme cards
                    formatted_response, matched = format_response_with_cards(response, SCHEME_DB, dm)
                    st.markdown(formatted_response, unsafe_allow_html=True)

                    # Generate and offer document checklist PDF if schemes found
                    if matched:
                        checklist_pdf = generate_checklist_pdf(matched)
                        st.download_button(
                            "📄 Download Document Checklist (PDF)",
                            data=checklist_pdf,
                            file_name=f"setu_checklist_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"checklist_{len(st.session_state.messages)}",
                        )

                    conf = result.get("overall_confidence", 0)
                    if conf > 0:
                        if conf >= 0.7: st.success(f"✅ Confidence: {conf:.0%} — Verified against official sources")
                        elif conf >= 0.4: st.warning(f"⚠️ Confidence: {conf:.0%} — Some claims need manual check")
                        else: st.error(f"❌ Confidence: {conf:.0%} — Please verify independently")
                else:
                    response = f"⚠️ Error: {payload}\n\nPlease ensure GROQ_API_KEY is set in your .env file or Streamlit secrets."
                    st.error(response)

            except Exception as e:
                progress_placeholder.empty()
                response = f"⚠️ Error: {str(e)}"
                st.error(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# ===== PAGE: EXPLORE SCHEMES =====
elif page == "🔍 Explore Schemes":
    st.markdown("## 🔍 Explore All Schemes")
    st.markdown(f"Browse **{len(SCHEME_DB)}** verified government schemes across **{len(set(s['level'] for s in SCHEME_DB))}** states and central government.")

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    all_cats = sorted(set(s["cat"] for s in SCHEME_DB))
    all_levels = sorted(set(s["level"] for s in SCHEME_DB))
    all_groups = sorted(set(s["group"] for s in SCHEME_DB))

    f_cat = fc1.selectbox("Filter by Type", ["All"] + all_cats)
    f_level = fc2.selectbox("Filter by Level", ["All"] + all_levels)
    f_search = fc3.text_input("🔍 Search schemes", placeholder="Type scheme name...")

    filtered = SCHEME_DB
    if f_cat != "All": filtered = [s for s in filtered if s["cat"] == f_cat]
    if f_level != "All": filtered = [s for s in filtered if s["level"] == f_level]
    if f_search: filtered = [s for s in filtered if f_search.lower() in s["name"].lower() or f_search.lower() in s.get("benefits", "").lower()]

    st.markdown(f"**Showing {len(filtered)} of {len(SCHEME_DB)} schemes**")

    # Scheme cards
    for s in filtered:
        color = CAT_COLORS.get(s["cat"], "#666")
        income_text = f"Income limit: ₹{s['income_limit']:,}/year" if s["income_limit"] else "No income limit"
        docs = s.get("documents", "Check official portal")
        deadline = s.get("deadline", "Check official portal")
        helpline = s.get("helpline", "")
        helpline_html = f'<div style="margin-top:0.3rem;font-size:0.78rem;">📞 Helpline: <b>{helpline}</b></div>' if helpline else ""

        st.markdown(f"""
        <div class="scheme-card">
            <div class="scheme-name">{s['icon']} {s['name']}</div>
            <div class="scheme-meta">{s['level']} Government • {income_text} • 📅 {deadline}</div>
            <span class="scheme-tag" style="background:{color}20; color:{color}; border:1px solid {color}40;">{s['cat']}</span>
            <span class="scheme-tag" style="background:#FF993320; color:#C2410C; border:1px solid #FF993340;">{s['group']}</span>
            <div style="margin-top:0.5rem; font-size:0.88rem; color:{TEXT_SECONDARY};">💰 <b>Benefits:</b> {s['benefits']}</div>
            <details style="margin-top:0.5rem;">
                <summary style="font-size:0.82rem;cursor:pointer;color:#FF9933;font-weight:600;">📄 Documents & How to Apply</summary>
                <div style="font-size:0.82rem;margin-top:0.3rem;padding:0.5rem;background:{'#2a2a3e' if dm else '#FFF7ED'};border-radius:8px;">
                    <b>Documents needed:</b> {docs}<br/>
                    <b>Deadline:</b> {deadline}
                </div>
            </details>
            {helpline_html}
            <div style="margin-top:0.3rem; font-size:0.78rem;"><a href="{s['url']}" target="_blank" style="color:#3B82F6;">🔗 Official Portal</a></div>
        </div>""", unsafe_allow_html=True)


# ===== PAGE: COMPARE SCHEMES =====
elif page == "⚖️ Compare Schemes":
    st.markdown("## ⚖️ Compare Schemes Side-by-Side")
    st.markdown("Select 2-3 schemes to compare their eligibility, benefits, and documents.")

    scheme_names = [s["name"] for s in SCHEME_DB]
    cc1, cc2, cc3 = st.columns(3)
    s1 = cc1.selectbox("Scheme 1", ["(none)"] + scheme_names, key="cmp1")
    s2 = cc2.selectbox("Scheme 2", ["(none)"] + scheme_names, key="cmp2")
    s3 = cc3.selectbox("Scheme 3 (optional)", ["(none)"] + scheme_names, key="cmp3")

    selected = [s for s in [s1, s2, s3] if s != "(none)"]

    if len(selected) >= 2:
        schemes = [next(s for s in SCHEME_DB if s["name"] == name) for name in selected]

        # Comparison table
        st.markdown("### 📊 Comparison")

        # Build comparison data
        fields = [
            ("🏷️ Category", "cat"),
            ("🏛️ Level", "level"),
            ("👥 Target Group", "group"),
            ("💰 Benefits", "benefits"),
            ("💵 Income Limit", None),
            ("📄 Documents", "documents"),
            ("📅 Deadline", "deadline"),
            ("📞 Helpline", "helpline"),
        ]

        header = "| Feature |" + "|".join(f" **{s['icon']} {s['name'][:30]}** " for s in schemes) + "|"
        separator = "|---|" + "|".join("---" for _ in schemes) + "|"
        rows = [header, separator]

        for label, key in fields:
            row = f"| {label} |"
            for s in schemes:
                if key is None:  # Income limit special handling
                    val = f"₹{s['income_limit']:,}/yr" if s.get("income_limit") else "No limit"
                elif key == "helpline":
                    val = s.get(key, "N/A")
                elif key == "documents":
                    val = s.get(key, "Check portal")[:60] + "..."
                else:
                    val = s.get(key, "N/A")
                row += f" {val} |"
            rows.append(row)

        # Portal links row
        row = "| 🔗 Portal |"
        for s in schemes:
            row += f" [{s['url'].split('//')[1][:25]}]({s['url']}) |"
        rows.append(row)

        st.markdown("\n".join(rows))

        # Visual comparison cards
        st.markdown("### 🎴 Visual Cards")
        card_cols = st.columns(len(schemes))
        for col, s in zip(card_cols, schemes):
            color = CAT_COLORS.get(s["cat"], "#666")
            income_text = f"₹{s['income_limit']:,}/yr" if s.get("income_limit") else "No limit"
            col.markdown(f"""<div class="scheme-card" style="border-top:4px solid {color};">
                <div style="font-size:2rem;text-align:center;">{s['icon']}</div>
                <div class="scheme-name" style="text-align:center;">{s['name']}</div>
                <hr style="border-color:{color}40;"/>
                <div style="font-size:0.85rem;"><b>💰 Benefits:</b><br/>{s['benefits']}</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;"><b>💵 Income Limit:</b> {income_text}</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;"><b>👥 For:</b> {s['group']}</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;"><b>📅 Deadline:</b> {s.get('deadline', 'N/A')}</div>
                <div style="font-size:0.82rem;margin-top:0.5rem;"><b>📄 Documents:</b><br/>{s.get('documents', 'Check portal')}</div>
                <div style="text-align:center;margin-top:0.8rem;"><a href="{s['url']}" target="_blank" style="color:#3B82F6;font-weight:600;">🔗 Apply Now</a></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("👆 Select at least 2 schemes above to compare them side-by-side.")

        # Quick suggestions
        st.markdown("### 💡 Popular Comparisons")
        sugg_cols = st.columns(3)
        suggestions = [
            ("🏥 Health Schemes", "Ayushman Bharat vs Chiranjeevi"),
            ("🎓 Scholarship Options", "Central Sector vs Post-Matric SC"),
            ("💰 Loan Schemes", "MUDRA vs Stand-Up India"),
        ]
        for col, (title, desc) in zip(sugg_cols, suggestions):
            col.markdown(f"""<div class="scheme-card" style="text-align:center;">
                <div style="font-size:1.5rem;">{title.split()[0]}</div>
                <div style="font-weight:600;margin:0.3rem 0;">{title}</div>
                <div style="font-size:0.82rem;color:{TEXT_MUTED};">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ===== PAGE: ELIGIBILITY CHECK =====
elif page == "✅ Eligibility Check":
    st.markdown("## ✅ Quick Eligibility Check")
    st.markdown("Select a scheme and fill your details to get an instant eligibility assessment.")

    scheme_names = [s["name"] for s in SCHEME_DB]
    selected = st.selectbox("Select Scheme", scheme_names)
    scheme = next(s for s in SCHEME_DB if s["name"] == selected)

    st.markdown(f"""<div class="scheme-card">
        <div class="scheme-name">{scheme['icon']} {scheme['name']}</div>
        <div class="scheme-meta">{scheme['level']} • {scheme['cat']} • Target: {scheme['group']}</div>
        <div style="font-size:0.9rem; margin-top:0.3rem;">💰 {scheme['benefits']}</div>
        <div style="font-size:0.82rem; margin-top:0.3rem;">📄 <b>Documents:</b> {scheme.get('documents', 'Check portal')}</div>
        <div style="font-size:0.82rem; margin-top:0.3rem;">📅 <b>Deadline:</b> {scheme.get('deadline', 'Check portal')}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Fill Your Details")
    ec1, ec2 = st.columns(2)
    e_cat = ec1.selectbox("Your Category", ["SC", "ST", "OBC", "MBC", "EWS", "Minority", "General"], key="elig_cat")
    e_state = ec2.selectbox("Your State", ["Rajasthan", "Uttar Pradesh", "Bihar", "Madhya Pradesh", "Maharashtra", "Other"], key="elig_state")
    ec3, ec4 = st.columns(2)
    e_income = ec3.number_input("Annual Family Income (₹)", min_value=0, value=200000, step=10000, key="elig_income")
    e_gender = ec4.selectbox("Gender", ["Male", "Female", "Other"], key="elig_gender")

    if st.button("🔍 Check Eligibility", use_container_width=True, key="check_elig"):
        eligible = True
        reasons_yes = []
        reasons_no = []

        # Category check
        grp = scheme["group"]
        # Broad group matching
        open_groups = ["All", "Farmer", "Farmers", "Rural", "Girl Child", "Orphan", "Widow",
                       "BPL/SECC", "BPL/EWS/LIG", "BPL Women", "BPL Families", "BPL/AAY/PHH",
                       "Unorganized Workers (18-40)", "Micro Entrepreneurs", "Artisans/Craftspeople",
                       "Pregnant Women", "All (Rajasthan)", "Students (Bihar)", "Girl Child (UP)", "Women (21-60)"]
        if grp in open_groups:
            reasons_yes.append(f"✅ Open to your group ({grp})")
        elif e_cat in grp:
            reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "SC/ST/OBC" and e_cat in ["SC", "ST", "OBC"]:
            reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "SC/ST/OBC/MBC/EWS" and e_cat in ["SC", "ST", "OBC", "MBC", "EWS"]:
            reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "SC/ST/Women" and (e_cat in ["SC", "ST"] or e_gender == "Female"):
            reasons_yes.append(f"✅ Category/gender eligible for {grp}")
        elif "SC/ST/OBC/Minority" in grp and e_cat in ["SC", "ST", "OBC", "Minority"]:
            if "Girls" in grp:
                if e_gender == "Female":
                    reasons_yes.append(f"✅ Category ({e_cat}) + Female eligible")
                else:
                    reasons_no.append(f"❌ This scheme is for female students only")
                    eligible = False
            else:
                reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "MBC Girls":
            if e_cat == "MBC" and e_gender == "Female":
                reasons_yes.append("✅ MBC Female — eligible")
            else:
                reasons_no.append(f"❌ This scheme is for MBC female students")
                eligible = False
        else:
            reasons_no.append(f"❌ Category mismatch: scheme is for {grp}, you selected {e_cat}")
            eligible = False

        # Income check
        if scheme["income_limit"]:
            if e_income <= scheme["income_limit"]:
                reasons_yes.append(f"✅ Income ₹{e_income:,} is within limit of ₹{scheme['income_limit']:,}")
            else:
                reasons_no.append(f"❌ Income ₹{e_income:,} exceeds limit of ₹{scheme['income_limit']:,}")
                eligible = False
        else:
            reasons_yes.append("✅ No income restriction")

        # State check
        state_schemes = {"Rajasthan": "Rajasthan", "Uttar Pradesh": "Uttar Pradesh",
                         "Madhya Pradesh": "Madhya Pradesh", "Bihar": "Bihar"}
        scheme_state = None
        for st_name in state_schemes:
            if st_name in scheme["level"]:
                scheme_state = st_name
                break

        if scheme_state and e_state != scheme_state:
            reasons_no.append(f"❌ This is a {scheme_state} state scheme but you selected {e_state}")
            eligible = False
        elif scheme_state:
            reasons_yes.append(f"✅ You are from {scheme_state} — eligible for state scheme")
        else:
            reasons_yes.append("✅ Central scheme — available in all states")

        # Display result
        st.markdown("---")
        if eligible:
            st.success(f"### ✅ You appear ELIGIBLE for {scheme['name']}")
        else:
            st.error(f"### ❌ You may NOT be eligible for {scheme['name']}")

        for r in reasons_yes:
            st.markdown(f"<span style='color:#10B981; font-size:0.9rem;'>{r}</span>", unsafe_allow_html=True)
        for r in reasons_no:
            st.markdown(f"<span style='color:#EF4444; font-size:0.9rem;'>{r}</span>", unsafe_allow_html=True)

        st.markdown(f"\n🔗 [Visit Official Portal]({scheme['url']})")

        # Document checklist
        if eligible and scheme.get("documents"):
            st.markdown("### 📄 Document Checklist")
            for doc in scheme["documents"].split(", "):
                st.checkbox(doc, key=f"doc_{doc[:20]}")

        # Helpline
        if scheme.get("helpline"):
            st.info(f"📞 **Helpline:** {scheme['helpline']} — Call for more details")

        st.warning("⚠️ This is a preliminary check. Please verify eligibility criteria on the official portal before applying.")


# ===== PAGE: DOCUMENT CHECKLIST =====
elif page == "📄 Document Checklist":
    st.markdown("## 📄 Document Checklist Generator")
    st.markdown("Select schemes you're applying for and get a **printable PDF checklist** with all required documents, portal links, and helpline numbers.")

    # Scheme selection
    scheme_names = [s["name"] for s in SCHEME_DB]
    selected_schemes = st.multiselect(
        "Select schemes to generate checklist for:",
        scheme_names,
        default=st.session_state.schemes_discussed[:3] if st.session_state.schemes_discussed else [],
        max_selections=8,
    )

    if selected_schemes:
        matched = [s for s in SCHEME_DB if s["name"] in selected_schemes]

        # Preview
        st.markdown(f"### 📋 Checklist Preview — {len(matched)} Schemes")

        # Collect all unique documents
        all_docs = set()
        for s in matched:
            for doc in s.get("documents", "").split(", "):
                if doc.strip():
                    all_docs.add(doc.strip())

        # Summary cards
        for s in matched:
            color = CAT_COLORS.get(s["cat"], "#666")
            docs = s.get("documents", "Check official portal")
            st.markdown(f"""<div class="scheme-card" style="border-left:4px solid {color};">
                <div class="scheme-name">{s['icon']} {s['name']}</div>
                <div style="font-size:0.85rem;margin:0.3rem 0;">💰 {s['benefits']}</div>
                <div style="font-size:0.82rem;color:{TEXT_MUTED};">📅 Deadline: {s.get('deadline', 'Check portal')}</div>
                <div style="font-size:0.82rem;margin-top:0.3rem;"><b>📄 Documents:</b> {docs}</div>
                <div style="font-size:0.78rem;margin-top:0.3rem;"><a href="{s['url']}" target="_blank" style="color:#3B82F6;">🔗 {s['url']}</a></div>
                {f'<div style="font-size:0.78rem;margin-top:0.2rem;">📞 Helpline: <b>{s.get("helpline")}</b></div>' if s.get('helpline') else ''}
            </div>""", unsafe_allow_html=True)

        # Document summary
        st.markdown("### 📝 All Documents You Need")
        st.markdown(f"**{len(all_docs)} unique documents** required across {len(matched)} schemes:")
        for doc in sorted(all_docs):
            st.checkbox(doc, key=f"cl_{doc[:25]}")

        # PDF download
        st.markdown("---")
        checklist_pdf = generate_checklist_pdf(matched)
        dc1, dc2 = st.columns(2)
        dc1.download_button(
            "📥 Download Checklist (PDF)",
            data=checklist_pdf,
            file_name=f"setu_document_checklist_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        # Text version
        text_lines = ["SETU — Document Checklist\n"]
        for s in matched:
            text_lines.append(f"\n{'='*50}")
            text_lines.append(f"{s['name']}")
            text_lines.append(f"  Benefits: {s.get('benefits', 'N/A')}")
            text_lines.append(f"  Deadline: {s.get('deadline', 'Check portal')}")
            text_lines.append(f"  Documents: {s.get('documents', 'Check portal')}")
            text_lines.append(f"  Portal: {s.get('url', 'N/A')}")
            if s.get("helpline"):
                text_lines.append(f"  Helpline: {s['helpline']}")
        dc2.download_button(
            "📄 Download Checklist (TXT)",
            data="\n".join(text_lines),
            file_name=f"setu_document_checklist_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.info("💡 **Tip:** Print this checklist and take it to your nearest CSC center or government office for assistance.")
    else:
        st.info("👆 Select one or more schemes above to generate your document checklist.")

        # Quick shortcuts based on discussed schemes
        if st.session_state.schemes_discussed:
            st.markdown("### 💡 Based on Your Chat")
            st.markdown(f"You discussed these schemes: **{', '.join(st.session_state.schemes_discussed[:5])}**")
            st.markdown("Select them above to generate a checklist!")


# ===== PAGE: DEADLINES =====
elif page == "📅 Deadlines":
    st.markdown("## 📅 Scheme Deadlines & Calendar")
    st.markdown("See application deadlines for all schemes at a glance. Never miss a deadline!")

    # Current month highlight
    now = datetime.datetime.now()
    current_month = now.strftime("%B %Y")
    st.markdown(f"""<div style="background:linear-gradient(135deg, #FF9933, #F5A623); padding:1rem 1.5rem; border-radius:16px; text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:1.5rem; color:white;">📅</div>
        <div style="font-size:1.1rem; font-weight:700; color:white;">{current_month}</div>
        <div style="font-size:0.85rem; color:rgba(255,255,255,0.9);">Check which schemes are open for applications right now</div>
    </div>""", unsafe_allow_html=True)

    # Categorize deadlines
    open_ongoing = [s for s in SCHEME_DB if "Open" in s.get("deadline", "") or "ongoing" in s.get("deadline", "").lower()]
    seasonal = [s for s in SCHEME_DB if s not in open_ongoing]

    # Open / Ongoing schemes
    st.markdown(f'<div class="section-header">🟢 Always Open ({len(open_ongoing)} schemes)</div>', unsafe_allow_html=True)
    st.markdown("These schemes accept applications year-round:")

    oc1, oc2 = st.columns(2)
    for idx, s in enumerate(open_ongoing):
        col = oc1 if idx % 2 == 0 else oc2
        color = CAT_COLORS.get(s["cat"], "#666")
        col.markdown(f"""<div style="background:{CARD_BG};border-left:3px solid #10B981;border-radius:0 10px 10px 0;padding:0.6rem 0.8rem;margin:0.3rem 0;font-size:0.85rem;color:{CARD_TEXT};">
            {s['icon']} <b>{s['name'][:40]}</b><br/>
            <span style="font-size:0.75rem;color:{TEXT_MUTED};">{s['cat']} • {s.get('deadline', 'Open')}</span>
        </div>""", unsafe_allow_html=True)

    # Seasonal / dated schemes
    if seasonal:
        st.markdown(f'<div class="section-header">📆 Seasonal Deadlines ({len(seasonal)} schemes)</div>', unsafe_allow_html=True)
        st.markdown("These schemes have specific application windows:")

        # Sort by deadline text for grouping
        months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        for s in seasonal:
            color = CAT_COLORS.get(s["cat"], "#666")
            deadline = s.get("deadline", "Check portal")

            # Determine urgency
            is_urgent = any(m in deadline for m in [now.strftime("%b"), months_order[(now.month) % 12]])
            border_color = "#EF4444" if is_urgent else color

            urgent_badge = '<span style="background:#EF4444;color:white;padding:2px 8px;border-radius:10px;font-size:0.7rem;font-weight:700;margin-left:0.5rem;">⚡ APPLY NOW</span>' if is_urgent else ""

            st.markdown(f"""<div class="scheme-card" style="border-left:4px solid {border_color};">
                <div class="scheme-name">{s['icon']} {s['name']} {urgent_badge}</div>
                <div style="font-size:0.88rem;color:{TEXT_SECONDARY};margin:0.3rem 0;">
                    📅 <b>Deadline:</b> {deadline} &nbsp;&nbsp;•&nbsp;&nbsp; 💰 {s['benefits']}
                </div>
                <div style="font-size:0.82rem;color:{TEXT_MUTED};">{s['level']} • {s['group']}</div>
                <div style="font-size:0.78rem;margin-top:0.3rem;"><a href="{s['url']}" target="_blank" style="color:#3B82F6;">🔗 Apply on official portal</a></div>
            </div>""", unsafe_allow_html=True)

    # Monthly overview
    st.markdown('<div class="section-header">📊 Monthly Application Windows</div>', unsafe_allow_html=True)
    month_data = {}
    for s in SCHEME_DB:
        dl = s.get("deadline", "")
        for m in months_order:
            if m in dl:
                if m not in month_data:
                    month_data[m] = []
                month_data[m].append(s["name"])

    if month_data:
        for month in months_order:
            if month in month_data:
                current = " 👈 **NOW**" if month == now.strftime("%b") else ""
                schemes_list = ", ".join(month_data[month][:3])
                more = f" +{len(month_data[month])-3} more" if len(month_data[month]) > 3 else ""
                st.markdown(f"**{month}**{current}: {schemes_list}{more}")
    else:
        st.info("Most schemes in the database have open/ongoing application periods.")


# ===== PAGE: HELPLINES & CSC =====
elif page == "📞 Helplines & CSC":
    st.markdown("## 📞 Helpline Numbers & CSC Locator")
    st.markdown("**Toll-free helpline numbers** for all major government schemes and the **CSC center locator** to find your nearest Common Service Center.")

    # CSC Locator prominent link
    st.markdown(f"""<div style="background:linear-gradient(135deg, #FF9933, #F5A623); padding:1.5rem; border-radius:16px; text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:2rem; color:white;">📍</div>
        <div style="font-size:1.2rem; font-weight:700; color:white; margin:0.3rem 0;">Find Your Nearest CSC Center</div>
        <div style="font-size:0.85rem; color:rgba(255,255,255,0.9); margin-bottom:0.8rem;">Common Service Centers help you apply for schemes, get certificates, and more</div>
        <a href="https://locator.csccloud.in/" target="_blank" style="display:inline-block; padding:0.6rem 2rem; background:white; color:#C2410C; border-radius:25px; text-decoration:none; font-weight:700; font-size:0.9rem;">🔍 Open CSC Locator</a>
    </div>""", unsafe_allow_html=True)

    # Helpline cards
    st.markdown('<div class="section-header">📞 Scheme Helplines (Toll-Free)</div>', unsafe_allow_html=True)

    for hl in HELPLINES:
        url_html = f' • <a href="{hl["url"]}" target="_blank" style="color:#3B82F6;">Visit Portal</a>' if hl.get("url") else ""
        st.markdown(f"""<div class="helpline-card">
            <div style="font-size:2rem;">{hl['icon']}</div>
            <div>
                <div class="helpline-name">{hl['name']}</div>
                <div class="helpline-number">📞 {hl['number']}</div>
                <div class="helpline-desc">{hl['desc']}{url_html}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📱 Useful Apps")
    app_cols = st.columns(3)
    apps = [
        ("Mera Ration", "Track your ration entitlements & nearest FPS", "🍚"),
        ("UMANG", "400+ govt services in one app", "📱"),
        ("DigiLocker", "Store your certificates digitally", "📂"),
    ]
    for col, (name, desc, icon) in zip(app_cols, apps):
        col.markdown(f"""<div class="scheme-card" style="text-align:center;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:700;margin:0.3rem 0;">{name}</div>
            <div style="font-size:0.82rem;color:{TEXT_MUTED};">{desc}</div>
        </div>""", unsafe_allow_html=True)


# ===== PAGE: HOW IT WORKS =====
elif page == "ℹ️ How It Works":
    st.markdown("## ℹ️ How SETU Works")
    st.markdown(f"SETU uses **5 specialized AI agents** powered by **Llama 3.1 via Groq** to process your query across **{len(SCHEME_DB)} verified schemes**.")

    st.markdown("""<div style="display:flex; align-items:center; justify-content:center; gap:0.3rem; margin:1rem 0 2rem; flex-wrap:wrap;">
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:110px; text-align:center; background:#EEF2FF;">
            <span style="font-size:1.8rem;">🌐</span><span style="font-size:0.8rem; font-weight:700; color:#4338CA; -webkit-text-fill-color:#4338CA;">Language<br/>Detection</span></div>
        <span style="font-size:1.4rem; color:#9CA3AF; -webkit-text-fill-color:#9CA3AF;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:110px; text-align:center; background:#FFF7ED;">
            <span style="font-size:1.8rem;">🔍</span><span style="font-size:0.8rem; font-weight:700; color:#C2410C; -webkit-text-fill-color:#C2410C;">Scheme<br/>Matching</span></div>
        <span style="font-size:1.4rem; color:#9CA3AF; -webkit-text-fill-color:#9CA3AF;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:110px; text-align:center; background:#F0FDF4;">
            <span style="font-size:1.8rem;">✅</span><span style="font-size:0.8rem; font-weight:700; color:#166534; -webkit-text-fill-color:#166534;">Fact<br/>Verification</span></div>
        <span style="font-size:1.4rem; color:#9CA3AF; -webkit-text-fill-color:#9CA3AF;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:110px; text-align:center; background:#FDF2F8;">
            <span style="font-size:1.8rem;">💼</span><span style="font-size:0.8rem; font-weight:700; color:#BE185D; -webkit-text-fill-color:#BE185D;">Opportunity<br/>Search</span></div>
        <span style="font-size:1.4rem; color:#9CA3AF; -webkit-text-fill-color:#9CA3AF;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:110px; text-align:center; background:#FFFBEB;">
            <span style="font-size:1.8rem;">📝</span><span style="font-size:0.8rem; font-weight:700; color:#92400E; -webkit-text-fill-color:#92400E;">Action<br/>Plan</span></div>
    </div>""", unsafe_allow_html=True)

    agents_info = [
        ("🌐 Language & Intake Agent", "Detects Hindi/English, extracts structured user profile (category, state, income, education) from natural language. Supports multi-turn conversation memory.", "#4338CA"),
        ("🔍 Eligibility & Scheme Agent", f"Uses RAG (Retrieval Augmented Generation) to search document chunks in ChromaDB across {len(SCHEME_DB)} schemes. Constructs a prompt with retrieved context for Llama 3.1. Never answers from memory alone.", "#C2410C"),
        ("✅ Verification & Grounding Agent", "Independently verifies each claim using a deterministic formula: **confidence = 0.3 × citation + 0.3 × similarity + 0.4 × coverage**. Not an LLM self-assessment.", "#166534"),
        ("💼 Opportunity Agent", "Searches PMKVY skill training and NCS job portal data for relevant livelihood opportunities beyond just welfare schemes.", "#BE185D"),
        ("📝 Planner & Action Agent", "Creates actionable step-by-step plans with document checklists, portal links, helpline numbers, and draft messages the user can send to their local office.", "#92400E"),
    ]

    for name, desc, color in agents_info:
        st.markdown(f"""<div class="agent-card" style="border-left: 4px solid {color};">
            <div class="agent-name" style="color: {color} !important;">{name}</div>
            <div class="agent-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏗️ Technology Stack")
    tc1, tc2, tc3, tc4 = st.columns(4)
    for col, icon, name, desc in [
        (tc1, "🤖", "Llama 3.1 (Groq)", "8B parameter LLM"),
        (tc2, "🔗", "LangGraph", "Agent orchestration"),
        (tc3, "📊", "ChromaDB", "Vector database"),
        (tc4, "🖥️", "Streamlit", "Chat interface"),
    ]:
        col.markdown(f"""<div class="tech-card">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:600; font-size:0.9rem;">{name}</div>
            <div style="font-size:0.75rem; opacity:0.7;">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 SDG Alignment")
    for sdg, goal, how in [
        ("SDG 1", "No Poverty", "Connects BPL families to welfare pensions, housing, food security, MGNREGA"),
        ("SDG 4", "Quality Education", "Matches students with scholarships, education loans, skill training"),
        ("SDG 8", "Decent Work", "Links to PMKVY skill training, MUDRA loans, Stand-Up India, NCS jobs"),
        ("SDG 10", "Reduced Inequalities", "Targets SC, ST, OBC, minorities, widows, women, artisans"),
    ]:
        st.markdown(f"**{sdg} — {goal}**: {how}")

    st.markdown("---")
    st.markdown("### 📊 Database Stats")
    stats_cols = st.columns(4)
    stats_cols[0].metric("Total Schemes", len(SCHEME_DB))
    stats_cols[1].metric("States Covered", len(set(s["level"] for s in SCHEME_DB)))
    stats_cols[2].metric("Categories", len(set(s["cat"] for s in SCHEME_DB)))
    stats_cols[3].metric("With Helplines", sum(1 for s in SCHEME_DB if s.get("helpline")))
