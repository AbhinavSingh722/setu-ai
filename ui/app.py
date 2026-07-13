"""
SETU — Premium Multi-Page Chat Interface
Features: Multi-page nav, Profile form, Animated pipeline, Eligibility calculator,
          Conversation memory, Voice input (browser speech-to-text)
"""
import os, sys, json, time
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from agents.orchestrator import run_setu
from ingestion.chroma_store import SetuVectorStore

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="SETU - सेतु | AI Bridge to Your Rights",
    page_icon="🌉", layout="wide", initial_sidebar_state="expanded",
)

# ===== ALL CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+Devanagari:wght@300;400;500;600;700&display=swap');

:root {
    --saffron: #FF9933; --saffron-dark: #E8850A; --saffron-light: #FFB366;
    --amber: #F5A623; --green: #10B981; --red: #EF4444; --yellow: #F59E0B;
    --blue: #3B82F6; --purple: #8B5CF6;
}

.stApp { font-family: 'Inter', 'Noto Sans Devanagari', sans-serif !important; }
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    border-right: 1px solid rgba(255,153,51,0.2);
}
[data-testid="stSidebar"] * { color: #E8E0D8 !important; }
[data-testid="stSidebar"] .stMarkdown h3 { color: #FF9933 !important; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
[data-testid="stSidebar"] hr { border-color: rgba(255,153,51,0.2) !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { font-size: 0.95rem; }

/* Hero */
.hero-section {
    background: linear-gradient(135deg, #FF6B00 0%, #FF9933 30%, #FFB366 60%, #F5A623 100%);
    padding: 2.5rem 2rem 2rem; border-radius: 20px; margin-bottom: 2rem;
    color: white; text-align: center; position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(255,107,0,0.3);
}
.hero-section::before {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: heroGlow 8s ease-in-out infinite alternate;
}
@keyframes heroGlow { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(30px,-20px) scale(1.1); } }
.hero-section h1 { font-size: 2.8rem; font-weight: 800; margin: 0; text-shadow: 0 2px 8px rgba(0,0,0,0.15); position: relative; z-index: 1; }
.hero-sub { font-size: 1.1rem; opacity: 0.95; margin: 0.5rem 0 0.2rem; position: relative; z-index: 1; }
.hero-hindi { font-size: 0.95rem; opacity: 0.85; font-style: italic; position: relative; z-index: 1; }

/* Stats bar */
.stats-container { display: flex; justify-content: center; gap: 2rem; margin: 1.5rem 0 0; position: relative; z-index: 1; }
.stat-item { text-align: center; padding: 0.8rem 1.2rem; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); min-width: 110px; transition: transform 0.2s; }
.stat-item:hover { transform: translateY(-2px); background: rgba(255,255,255,0.22); }
.stat-number { font-size: 1.8rem; font-weight: 800; display: block; line-height: 1; }
.stat-label { font-size: 0.75rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* Section headers */
.section-header { font-size: 1.3rem; font-weight: 700; color: #FF6B00; margin: 1.5rem 0 1rem; display: flex; align-items: center; gap: 0.5rem; }
.section-header::after { content: ''; flex: 1; height: 2px; background: linear-gradient(90deg, #FF993380, transparent); margin-left: 0.5rem; }

/* Feature cards */
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem; }
.feature-card { background: linear-gradient(135deg, #fff 0%, #FFF8F0 100%); border: 1px solid #FFE0B2; border-radius: 16px; padding: 1.2rem; text-align: center; transition: all 0.3s; }
.feature-card:hover { transform: translateY(-4px); box-shadow: 0 8px 40px rgba(255,153,51,0.15); border-color: #FF9933; }
.feature-icon { font-size: 2rem; margin-bottom: 0.5rem; display: block; }
.feature-title { font-size: 0.9rem; font-weight: 600; color: #2D1B00; margin-bottom: 0.3rem; }
.feature-desc { font-size: 0.78rem; color: #8B7355; line-height: 1.4; }

/* Category pills */
.category-container { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 1.5rem; }
.cat-pill { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; border-radius: 25px; font-size: 0.82rem; font-weight: 500; border: 1.5px solid; transition: all 0.2s; }
.cat-pill:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.p-sch { background: #EEF2FF; border-color: #818CF8; color: #4338CA; }
.p-pen { background: #FEF3C7; border-color: #F59E0B; color: #B45309; }
.p-far { background: #D1FAE5; border-color: #34D399; color: #065F46; }
.p-wom { background: #FCE7F3; border-color: #F472B6; color: #BE185D; }
.p-skl { background: #E0E7FF; border-color: #6366F1; color: #3730A3; }
.p-emp { background: #ECFDF5; border-color: #10B981; color: #047857; }

/* Pipeline */
.pipeline-container { display: flex; align-items: center; justify-content: center; gap: 0.3rem; margin: 1rem 0 2rem; flex-wrap: wrap; }
.pipeline-step { display: flex; flex-direction: column; align-items: center; padding: 0.8rem 0.6rem; border-radius: 12px; min-width: 100px; text-align: center; transition: all 0.3s; }
.pipeline-step:hover { transform: translateY(-3px); }
.step-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
.step-name { font-size: 0.72rem; font-weight: 600; line-height: 1.2; }
.s1 { background: #EEF2FF; color: #4338CA !important; } .s1 * { color: #4338CA !important; }
.s2 { background: #FFF7ED; color: #C2410C !important; } .s2 * { color: #C2410C !important; }
.s3 { background: #F0FDF4; color: #166534 !important; } .s3 * { color: #166534 !important; }
.s4 { background: #FDF2F8; color: #BE185D !important; } .s4 * { color: #BE185D !important; }
.s5 { background: #FFFBEB; color: #92400E !important; } .s5 * { color: #92400E !important; }
.p-arrow { font-size: 1.2rem; color: #D1D5DB; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #FFFAF5, #FFF3E0) !important; color: #C2410C !important;
    border: 1.5px solid #FFCC80 !important; border-radius: 14px !important;
    padding: 0.8rem 1rem !important; font-size: 0.85rem !important; font-weight: 500 !important;
    transition: all 0.25s ease !important; text-align: left !important; line-height: 1.4 !important; min-height: 55px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FF9933, #F5A623) !important; color: white !important;
    border-color: #FF9933 !important; transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255,153,51,0.25) !important;
}

/* Chat animation */
[data-testid="stChatMessage"] { border-radius: 16px !important; margin-bottom: 0.5rem !important; animation: fadeInUp 0.4s ease; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Badges */
.badge-v { background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; margin: 3px 0; letter-spacing: 0.5px; }
.badge-r { background: linear-gradient(135deg, #F59E0B, #D97706); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; margin: 3px 0; letter-spacing: 0.5px; }
.badge-u { background: linear-gradient(135deg, #EF4444, #DC2626); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; margin: 3px 0; letter-spacing: 0.5px; }

/* Trace */
.trace-item { background: rgba(255,153,51,0.08); border-left: 3px solid #FF9933; padding: 0.6rem 0.8rem; margin: 0.4rem 0; border-radius: 0 10px 10px 0; font-size: 0.78rem; line-height: 1.4; transition: all 0.2s; }
.trace-item:hover { background: rgba(255,153,51,0.15); padding-left: 1rem; }

/* Confidence ring */
.conf-ring { width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-direction: column; margin: 1rem auto; }
.conf-val { font-size: 1.8rem; font-weight: 800; line-height: 1; }
.conf-lbl { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; }

/* Sidebar card */
.sb-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,153,51,0.15); border-radius: 12px; padding: 0.8rem; margin: 0.5rem 0; }
.sb-card h4 { color: #FFB366 !important; font-size: 0.85rem; margin: 0 0 0.4rem; }
.sb-card p { font-size: 0.78rem; opacity: 0.8; margin: 0; line-height: 1.5; }

/* Scheme cards for explorer — force light bg for dark mode */
.scheme-card { background: #FFFAF5 !important; border: 1px solid #FFE0B2; border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem; transition: all 0.3s; color: #2D1B00 !important; }
.scheme-card:hover { box-shadow: 0 8px 30px rgba(255,153,51,0.15); border-color: #FF9933; }
.scheme-card * { color: #2D1B00 !important; }
.scheme-name { font-size: 1.05rem; font-weight: 700; color: #C2410C !important; margin-bottom: 0.4rem; }
.scheme-meta { font-size: 0.78rem; color: #8B7355 !important; margin-bottom: 0.5rem; }
.scheme-tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; }

/* Agent info cards — force light bg */
.agent-card { background: #FFFAF5 !important; border-radius: 0 12px 12px 0; padding: 1rem 1.2rem; margin: 0.8rem 0; color: #2D1B00 !important; }
.agent-card * { color: #2D1B00 !important; }
.agent-card .agent-name { font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; }
.agent-card .agent-desc { font-size: 0.88rem; line-height: 1.5; }

/* Tech cards — force light */
.tech-card { text-align: center; padding: 1rem; background: #FFFAF5 !important; border-radius: 12px; border: 1px solid #FFE0B2; color: #2D1B00 !important; }
.tech-card * { color: #2D1B00 !important; }

/* Feature cards — force light */
.feature-card, .feature-card * { color: #2D1B00 !important; }
.feature-desc { color: #8B7355 !important; }

/* All custom HTML content — force readable in dark mode */
.setu-content { background: #FFFAF5 !important; color: #2D1B00 !important; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; }
.setu-content * { color: #2D1B00 !important; }

/* Pipeline steps — ensure visibility */
.pipeline-step, .pipeline-step * { color: inherit !important; }

/* Animated pipeline progress */
.progress-pipeline { display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin: 1rem 0; }
.prog-step { padding: 0.5rem 0.8rem; border-radius: 10px; font-size: 0.75rem; font-weight: 600; text-align: center; min-width: 80px; transition: all 0.3s; }
.prog-active { background: #FF9933; color: white !important; animation: pulse 1.5s infinite; box-shadow: 0 0 20px rgba(255,153,51,0.4); }
.prog-done { background: #10B981; color: white !important; }
.prog-wait { background: #E5E7EB; color: #9CA3AF !important; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
.prog-arrow { color: #D1D5DB; font-size: 0.9rem; }

/* Footer */
.setu-footer { text-align: center; padding: 1.5rem; margin-top: 2rem; border-top: 1px solid rgba(255,153,51,0.15); font-size: 0.75rem; color: #8B7355; }

/* Profile form highlight */
.profile-badge { background: linear-gradient(135deg, #FF9933, #F5A623); color: white !important; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin: 2px; }

@media (max-width: 768px) {
    .hero-section h1 { font-size: 1.8rem; }
    .stats-container { gap: 0.5rem; }
    .stat-item { min-width: 75px; padding: 0.5rem; }
    .stat-number { font-size: 1.3rem; }
    .feature-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ===== VOICE INPUT (Streamlit-native approach) =====
# Voice uses a hidden text input + JS that fills it, then auto-submits
# This avoids the broken chat_input injection approach

# ===== SESSION STATE =====
defaults = {
    "messages": [], "agent_trace": [], "verification_data": None,
    "user_profile": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ===== SCHEME DATA (for explorer + calculator) =====
SCHEME_DB = [
    {"name": "Post-Matric Scholarship for SC Students", "cat": "Scholarship", "group": "SC", "level": "Central", "icon": "🎓",
     "benefits": "Full tuition + maintenance allowance", "income_limit": 250000, "url": "https://scholarships.gov.in"},
    {"name": "Post-Matric Scholarship for ST Students", "cat": "Scholarship", "group": "ST", "level": "Central", "icon": "🎓",
     "benefits": "Full tuition + maintenance allowance", "income_limit": 250000, "url": "https://scholarships.gov.in"},
    {"name": "Pre-Matric Scholarship for Minorities", "cat": "Scholarship", "group": "Minority", "level": "Central", "icon": "🎓",
     "benefits": "Admission + tuition + maintenance", "income_limit": 100000, "url": "https://scholarships.gov.in"},
    {"name": "Post-Matric Scholarship for OBC", "cat": "Scholarship", "group": "OBC", "level": "Central", "icon": "🎓",
     "benefits": "Tuition + exam fees + maintenance", "income_limit": 100000, "url": "https://scholarships.gov.in"},
    {"name": "NMMSS Scholarship", "cat": "Scholarship", "group": "All", "level": "Central", "icon": "🏅",
     "benefits": "Rs 12,000/year for Class 9-12", "income_limit": 350000, "url": "https://scholarships.gov.in"},
    {"name": "Central Sector Scholarship (CSSS)", "cat": "Scholarship", "group": "All", "level": "Central", "icon": "🎓",
     "benefits": "Rs 10,000-20,000/year for UG/PG", "income_limit": 800000, "url": "https://scholarships.gov.in"},
    {"name": "PM Kisan Samman Nidhi", "cat": "Welfare", "group": "Farmer", "level": "Central", "icon": "🌾",
     "benefits": "Rs 6,000/year in 3 instalments", "income_limit": None, "url": "https://pmkisan.gov.in"},
    {"name": "Sukanya Samriddhi Yojana", "cat": "Savings", "group": "Girl Child", "level": "Central", "icon": "👧",
     "benefits": "8.2% interest, tax-free maturity", "income_limit": None, "url": "https://www.nsiindia.gov.in"},
    {"name": "MGNREGA", "cat": "Employment", "group": "Rural", "level": "Central", "icon": "👷",
     "benefits": "100 days guaranteed employment", "income_limit": None, "url": "https://nrega.nic.in"},
    {"name": "Indira Gandhi Widow Pension", "cat": "Pension", "group": "Widow", "level": "Central", "icon": "👵",
     "benefits": "Rs 300-500/month pension", "income_limit": None, "url": "https://nsap.nic.in"},
    {"name": "Rajasthan CM Scholarship", "cat": "Scholarship", "group": "SC/ST/OBC", "level": "Rajasthan", "icon": "🎓",
     "benefits": "Rs 5,000-10,000/year", "income_limit": 250000, "url": "https://sje.rajasthan.gov.in"},
    {"name": "Rajasthan Uttar Matric Scholarship", "cat": "Scholarship", "group": "SC/ST/OBC", "level": "Rajasthan", "icon": "🎓",
     "benefits": "100% tuition reimbursement", "income_limit": 250000, "url": "https://sje.rajasthan.gov.in"},
    {"name": "Rajasthan Palanhar Yojana", "cat": "Welfare", "group": "Orphan", "level": "Rajasthan", "icon": "🏠",
     "benefits": "Rs 500-1000/month per child", "income_limit": 120000, "url": "https://sje.rajasthan.gov.in"},
    {"name": "Anuprati Coaching Yojana", "cat": "Scholarship", "group": "SC/ST/OBC/MBC/EWS", "level": "Rajasthan", "icon": "📚",
     "benefits": "Free competitive exam coaching", "income_limit": 800000, "url": "https://sje.rajasthan.gov.in"},
    {"name": "Devnarayan Scooty Yojana", "cat": "Incentive", "group": "MBC Girls", "level": "Rajasthan", "icon": "🛵",
     "benefits": "Free scooty for meritorious girls", "income_limit": 250000, "url": "https://hte.rajasthan.gov.in"},
    {"name": "Kali Bai Scooty Yojana", "cat": "Incentive", "group": "SC/ST/OBC/Minority Girls", "level": "Rajasthan", "icon": "🛵",
     "benefits": "Free scooty for 12th pass girls", "income_limit": 250000, "url": "https://hte.rajasthan.gov.in"},
    {"name": "PMKVY Skill Training", "cat": "Skill", "group": "All", "level": "Central", "icon": "💻",
     "benefits": "Free skill training + certificate", "income_limit": None, "url": "https://skillindiadigital.gov.in"},
    {"name": "NCS Job Portal", "cat": "Employment", "group": "All", "level": "Central", "icon": "💼",
     "benefits": "Free job matching & career services", "income_limit": None, "url": "https://ncs.gov.in"},
]

CAT_COLORS = {"Scholarship": "#4338CA", "Welfare": "#B45309", "Savings": "#059669",
              "Employment": "#047857", "Pension": "#BE185D", "Incentive": "#7C3AED",
              "Skill": "#3730A3"}


# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:1rem 0 0.5rem;">
        <span style="font-size:2.5rem;">🌉</span>
        <div style="font-size:1.2rem; font-weight:700; color:#FF9933!important; margin-top:0.3rem;">SETU — सेतु</div>
        <div style="font-size:0.7rem; opacity:0.6;">AI-Powered Scheme Discovery</div>
    </div>""", unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation — check for pending nav from buttons (must be BEFORE radio)
    PAGES = ["🏠 Home", "💬 Chat", "🔍 Explore Schemes", "✅ Eligibility Check", "ℹ️ How It Works"]
    if "_goto" in st.session_state:
        st.session_state.nav_page = st.session_state._goto
        del st.session_state._goto
    
    st.markdown("### 🧭 Navigate")
    page = st.radio("", PAGES, key="nav_page", label_visibility="collapsed")
    
    st.divider()
    
    # User Profile Summary (conversation memory)
    if st.session_state.user_profile:
        st.markdown("### 👤 Your Profile")
        p = st.session_state.user_profile
        badges = []
        if p.get("category"): badges.append(p["category"])
        if p.get("state"): badges.append(p["state"])
        if p.get("income"): badges.append(f"Income: {p['income']}")
        if p.get("education"): badges.append(p["education"])
        if p.get("gender"): badges.append(p["gender"])
        for b in badges:
            st.markdown(f'<span class="profile-badge">{b}</span>', unsafe_allow_html=True)
        if st.button("Clear Profile", key="clear_profile"):
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
    st.markdown("""<div class="sb-card"><p>
    🤖 <b>IBM Granite 3.3</b> local<br/>📚 <b>18 schemes</b> verified<br/>
    ✅ <b>Cited claims</b><br/>🌐 <b>Hindi + English</b><br/>🏛️ <b>SDG 1,4,8,10</b>
    </p></div>""", unsafe_allow_html=True)


# ===== PAGE: HOME =====
if page == "🏠 Home":
    st.markdown("""<div class="hero-section">
        <h1>🌉 SETU — सेतु</h1>
        <p class="hero-sub">AI Bridge to Your Rights, Schemes & Opportunities</p>
        <p class="hero-hindi">अपने अधिकारों, योजनाओं और अवसरों तक AI पुल</p>
        <div class="stats-container">
            <div class="stat-item"><span class="stat-number">18</span><span class="stat-label">Schemes</span></div>
            <div class="stat-item"><span class="stat-number">5</span><span class="stat-label">AI Agents</span></div>
            <div class="stat-item"><span class="stat-number">2</span><span class="stat-label">Languages</span></div>
            <div class="stat-item"><span class="stat-number">100%</span><span class="stat-label">Cited</span></div>
        </div></div>""", unsafe_allow_html=True)
    
    # Features
    st.markdown('<div class="section-header">✨ What SETU Can Do</div>', unsafe_allow_html=True)
    st.markdown("""<div class="feature-grid">
        <div class="feature-card"><span class="feature-icon">🎓</span><div class="feature-title">Find Scholarships</div><div class="feature-desc">SC, ST, OBC, Minority — national & state</div></div>
        <div class="feature-card"><span class="feature-icon">🛡️</span><div class="feature-title">Verify Claims</div><div class="feature-desc">Every recommendation checked against sources</div></div>
        <div class="feature-card"><span class="feature-icon">📋</span><div class="feature-title">Action Plans</div><div class="feature-desc">Step-by-step with documents & draft messages</div></div>
        <div class="feature-card"><span class="feature-icon">🎤</span><div class="feature-title">Voice Input</div><div class="feature-desc">Speak in Hindi or English — no typing needed</div></div>
        <div class="feature-card"><span class="feature-icon">👤</span><div class="feature-title">Profile Memory</div><div class="feature-desc">Fill once, auto-applies to all queries</div></div>
        <div class="feature-card"><span class="feature-icon">✅</span><div class="feature-title">Eligibility Check</div><div class="feature-desc">Instant yes/no for any specific scheme</div></div>
    </div>""", unsafe_allow_html=True)
    
    # Categories
    st.markdown('<div class="section-header">📂 Scheme Categories</div>', unsafe_allow_html=True)
    st.markdown("""<div class="category-container">
        <span class="cat-pill p-sch">🎓 SC/ST Scholarships</span><span class="cat-pill p-sch">📖 OBC Scholarships</span>
        <span class="cat-pill p-sch">🕌 Minority Scholarships</span><span class="cat-pill p-pen">👵 Widow Pension</span>
        <span class="cat-pill p-far">🌾 PM Kisan</span><span class="cat-pill p-emp">👷 MGNREGA</span>
        <span class="cat-pill p-wom">👧 Girl Child Savings</span><span class="cat-pill p-wom">🛵 Scooty Schemes</span>
        <span class="cat-pill p-skl">💻 PMKVY Training</span><span class="cat-pill p-skl">💼 NCS Jobs</span>
    </div>""", unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<div class="section-header">🚀 Get Started</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("💬 Start Chatting", use_container_width=True, key="go_chat"):
        st.session_state._goto = "💬 Chat"; st.rerun()
    if c2.button("🔍 Browse Schemes", use_container_width=True, key="go_explore"):
        st.session_state._goto = "🔍 Explore Schemes"; st.rerun()
    if c3.button("✅ Check Eligibility", use_container_width=True, key="go_elig"):
        st.session_state._goto = "✅ Eligibility Check"; st.rerun()
    
    st.markdown("""<div class="setu-footer">🌉 SETU — <em>Building bridges to rights and opportunities</em><br/>
        Powered by <b>IBM Granite 3.3</b> • <b>LangGraph</b> • <b>ChromaDB</b> |
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
    
    # Voice input — Streamlit-native approach using text_input
    with st.expander("🎤 **Voice Input** (speak in Hindi or English)", expanded=False):
        st.markdown("""
        <div style="background:#FFFAF5; padding:1rem; border-radius:12px; border:1px solid #FFE0B2; color:#2D1B00;">
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
    
    # Example queries
    if not st.session_state.messages:
        st.markdown('<div class="section-header">💡 Try Asking</div>', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        examples = [
            ("🎓", "I am an SC student from Rajasthan, income 2 lakh. What scholarships can I get?"),
            ("👵", "मैं एक विधवा हूँ, BPL परिवार से। कौन सी पेंशन योजना है?"),
            ("🌾", "I'm a farmer with 2 acres. What government schemes are available?"),
            ("👧", "मेरी बेटी 5 साल की है। उसके लिए कौन सी बचत योजना है?"),
        ]
        for i, (ic, q) in enumerate(examples):
            col = ec1 if i % 2 == 0 else ec2
            if col.button(f"{ic}  {q}", key=f"ex_{i}", use_container_width=True):
                st.session_state.pending_query = q; st.rerun()
    
    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🙋" if msg["role"] == "user" else "🌉"):
            st.markdown(msg["content"])
    
    # Chat input
    user_input = None
    if "pending_query" in st.session_state:
        user_input = st.session_state.pending_query
        del st.session_state.pending_query
    else:
        user_input = st.chat_input("Ask about schemes... / योजनाओं के बारे में पूछें...")
    
    if user_input:
        # Append profile context to query
        profile = st.session_state.user_profile
        if profile:
            ctx = ", ".join(f"{k}: {v}" for k, v in profile.items())
            enhanced = f"{user_input}\n\n[User profile: {ctx}]"
        else:
            enhanced = user_input
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(user_input)
        
        with st.chat_message("assistant", avatar="🌉"):
            # Animated pipeline progress
            progress_placeholder = st.empty()
            agents = ["Language", "Eligibility", "Verification", "Opportunity", "Planner"]
            
            def show_progress(active_idx):
                steps_html = '<div class="progress-pipeline">'
                for i, a in enumerate(agents):
                    if i < active_idx: cls = "prog-done"
                    elif i == active_idx: cls = "prog-active"
                    else: cls = "prog-wait"
                    steps_html += f'<div class="prog-step {cls}">{a}</div>'
                    if i < len(agents) - 1: steps_html += '<span class="prog-arrow">→</span>'
                steps_html += '</div>'
                progress_placeholder.markdown(steps_html, unsafe_allow_html=True)
            
            show_progress(0)
            
            try:
                # Simulate progress updates (real processing happens in run_setu)
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
                
                # Animate progress while waiting
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
                    st.markdown(response)
                    
                    conf = result.get("overall_confidence", 0)
                    if conf > 0:
                        if conf >= 0.7: st.success(f"✅ Confidence: {conf:.0%} — Verified against official sources")
                        elif conf >= 0.4: st.warning(f"⚠️ Confidence: {conf:.0%} — Some claims need manual check")
                        else: st.error(f"❌ Confidence: {conf:.0%} — Please verify independently")
                else:
                    response = f"⚠️ Error: {payload}\n\nEnsure Ollama is running with granite3.3:8b."
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
    st.markdown("Browse the 18 verified government schemes in our database.")
    
    # Filters
    fc1, fc2, fc3 = st.columns(3)
    f_cat = fc1.selectbox("Filter by Type", ["All"] + list(set(s["cat"] for s in SCHEME_DB)))
    f_level = fc2.selectbox("Filter by Level", ["All", "Central", "Rajasthan"])
    f_group = fc3.selectbox("Filter by Group", ["All"] + sorted(set(s["group"] for s in SCHEME_DB)))
    
    filtered = SCHEME_DB
    if f_cat != "All": filtered = [s for s in filtered if s["cat"] == f_cat]
    if f_level != "All": filtered = [s for s in filtered if s["level"] == f_level]
    if f_group != "All": filtered = [s for s in filtered if s["group"] == f_group]
    
    st.markdown(f"**Showing {len(filtered)} of {len(SCHEME_DB)} schemes**")
    
    # Scheme cards
    for s in filtered:
        color = CAT_COLORS.get(s["cat"], "#666")
        income_text = f"Income limit: ₹{s['income_limit']:,}/year" if s["income_limit"] else "No income limit"
        st.markdown(f"""
        <div class="scheme-card">
            <div class="scheme-name">{s['icon']} {s['name']}</div>
            <div class="scheme-meta">{s['level']} Government • {income_text}</div>
            <span class="scheme-tag" style="background:{color}20; color:{color}; border:1px solid {color}40;">{s['cat']}</span>
            <span class="scheme-tag" style="background:#FF993320; color:#C2410C; border:1px solid #FF993340;">{s['group']}</span>
            <div style="margin-top:0.5rem; font-size:0.88rem; color:#4B5563;">💰 <b>Benefits:</b> {s['benefits']}</div>
            <div style="margin-top:0.3rem; font-size:0.78rem;"><a href="{s['url']}" target="_blank" style="color:#3B82F6;">🔗 Official Portal</a></div>
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
    </div>""", unsafe_allow_html=True)
    
    st.markdown("### Fill Your Details")
    ec1, ec2 = st.columns(2)
    e_cat = ec1.selectbox("Your Category", ["SC", "ST", "OBC", "MBC", "EWS", "Minority", "General"], key="elig_cat")
    e_state = ec2.selectbox("Your State", ["Rajasthan", "Uttar Pradesh", "Bihar", "MP", "Maharashtra", "Other"], key="elig_state")
    ec3, ec4 = st.columns(2)
    e_income = ec3.number_input("Annual Family Income (₹)", min_value=0, value=200000, step=10000, key="elig_income")
    e_gender = ec4.selectbox("Gender", ["Male", "Female", "Other"], key="elig_gender")
    
    if st.button("🔍 Check Eligibility", use_container_width=True, key="check_elig"):
        eligible = True
        reasons_yes = []
        reasons_no = []
        
        # Category check
        grp = scheme["group"]
        if grp in ["All", "Farmer", "Rural", "Girl Child", "Orphan", "Widow"]:
            reasons_yes.append(f"✅ Open to all / your group ({grp})")
        elif e_cat in grp:
            reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "SC/ST/OBC" and e_cat in ["SC", "ST", "OBC"]:
            reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "SC/ST/OBC/MBC/EWS" and e_cat in ["SC", "ST", "OBC", "MBC", "EWS"]:
            reasons_yes.append(f"✅ Your category ({e_cat}) is eligible")
        elif grp == "SC/ST/OBC/Minority Girls" and e_cat in ["SC", "ST", "OBC", "Minority"]:
            if e_gender == "Female":
                reasons_yes.append(f"✅ Category ({e_cat}) + Female eligible")
            else:
                reasons_no.append(f"❌ This scheme is for female students only")
                eligible = False
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
        if scheme["level"] == "Rajasthan" and e_state != "Rajasthan":
            reasons_no.append(f"❌ This is a Rajasthan state scheme but you selected {e_state}")
            eligible = False
        elif scheme["level"] == "Rajasthan":
            reasons_yes.append("✅ You are from Rajasthan — eligible for state scheme")
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
        
        st.info("⚠️ This is a preliminary check. Please verify eligibility criteria on the official portal before applying.")


# ===== PAGE: HOW IT WORKS =====
elif page == "ℹ️ How It Works":
    st.markdown("## ℹ️ How SETU Works")
    st.markdown("SETU uses **5 specialized AI agents** powered by **IBM Granite 3.3** to process your query.")
    
    st.markdown("""<div style="display:flex; align-items:center; justify-content:center; gap:0.3rem; margin:1rem 0 2rem; flex-wrap:wrap;">
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:100px; text-align:center; background:#EEF2FF;">
            <span style="font-size:1.5rem;">🌐</span><span style="font-size:0.72rem; font-weight:600; color:#4338CA !important;">Language<br/>Detection</span></div>
        <span style="font-size:1.2rem; color:#D1D5DB;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:100px; text-align:center; background:#FFF7ED;">
            <span style="font-size:1.5rem;">🔍</span><span style="font-size:0.72rem; font-weight:600; color:#C2410C !important;">Scheme<br/>Matching</span></div>
        <span style="font-size:1.2rem; color:#D1D5DB;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:100px; text-align:center; background:#F0FDF4;">
            <span style="font-size:1.5rem;">✅</span><span style="font-size:0.72rem; font-weight:600; color:#166534 !important;">Fact<br/>Verification</span></div>
        <span style="font-size:1.2rem; color:#D1D5DB;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:100px; text-align:center; background:#FDF2F8;">
            <span style="font-size:1.5rem;">💼</span><span style="font-size:0.72rem; font-weight:600; color:#BE185D !important;">Opportunity<br/>Search</span></div>
        <span style="font-size:1.2rem; color:#D1D5DB;">→</span>
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.8rem 0.6rem; border-radius:12px; min-width:100px; text-align:center; background:#FFFBEB;">
            <span style="font-size:1.5rem;">📝</span><span style="font-size:0.72rem; font-weight:600; color:#92400E !important;">Action<br/>Plan</span></div>
    </div>""", unsafe_allow_html=True)
    
    agents_info = [
        ("🌐 Language & Intake Agent", "Detects Hindi/English, extracts structured user profile (category, state, income, education) from natural language.", "#4338CA"),
        ("🔍 Eligibility & Scheme Agent", "Uses RAG (Retrieval Augmented Generation) to search 98 document chunks in ChromaDB. Constructs a prompt with retrieved context for IBM Granite. Never answers from memory alone.", "#C2410C"),
        ("✅ Verification & Grounding Agent", "Independently verifies each claim using a deterministic formula: **confidence = 0.3 × citation + 0.3 × similarity + 0.4 × coverage**. Not an LLM self-assessment.", "#166534"),
        ("💼 Opportunity Agent", "Searches PMKVY skill training and NCS job portal data for relevant livelihood opportunities beyond just welfare schemes.", "#BE185D"),
        ("📝 Planner & Action Agent", "Creates actionable step-by-step plans with document checklists, portal links, and draft messages the user can send to their local office.", "#92400E"),
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
        (tc1, "🤖", "IBM Granite 3.3", "8B parameter LLM"),
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
        ("SDG 1", "No Poverty", "Connects BPL families to welfare pensions, MGNREGA"),
        ("SDG 4", "Quality Education", "Matches students with scholarships"),
        ("SDG 8", "Decent Work", "Links to PMKVY skill training, NCS jobs"),
        ("SDG 10", "Reduced Inequalities", "Targets SC, ST, OBC, minorities, widows"),
    ]:
        st.markdown(f"**{sdg} — {goal}**: {how}")
