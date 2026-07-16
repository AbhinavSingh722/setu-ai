"""
Generate SETU AI Lean Canvas — Professional PPT for IBM SkillsBuild Submission
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ─── Configuration ───
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SETU_Lean_Canvas.pptx")

# Colors
INDIGO      = RGBColor(0x43, 0x38, 0xCA)
DARK_BG     = RGBColor(0x0F, 0x17, 0x2A)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY  = RGBColor(0xF1, 0xF5, 0xF9)
MID_GRAY    = RGBColor(0x94, 0xA3, 0xB8)
DARK_TEXT    = RGBColor(0x1E, 0x29, 0x3B)
ACCENT_ORANGE = RGBColor(0xF5, 0x9E, 0x0B)
ACCENT_GREEN  = RGBColor(0x10, 0xB9, 0x81)
ACCENT_RED    = RGBColor(0xEF, 0x44, 0x44)
ACCENT_BLUE   = RGBColor(0x38, 0x82, 0xF6)
ACCENT_PINK   = RGBColor(0xEC, 0x48, 0x99)
CARD_BG       = RGBColor(0x1E, 0x29, 0x3B)
CARD_BORDER   = RGBColor(0x33, 0x41, 0x55)

def add_rounded_rect(slide, left, top, width, height, fill_color, border_color=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    # Rounded corner
    shape.adjustments[0] = 0.05
    return shape

def add_text_box(slide, left, top, width, height, text, font_size=9, bold=False, color=WHITE, alignment=PP_ALIGN.LEFT, font_name="Segoe UI"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_multiline_text(slide, left, top, width, height, lines, font_size=8, color=WHITE, bullet_color=None, font_name="Segoe UI"):
    """Add text with multiple lines/bullets."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = font_name
        p.space_after = Pt(2)
        p.space_before = Pt(1)
    return txBox

def add_header_with_icon(slide, left, top, width, icon, title, accent_color):
    """Add a section header with emoji icon and colored title."""
    # Icon
    add_text_box(slide, left + Inches(0.08), top + Inches(0.05), Inches(0.3), Inches(0.25),
                 icon, font_size=11, color=accent_color)
    # Title
    add_text_box(slide, left + Inches(0.35), top + Inches(0.07), width - Inches(0.4), Inches(0.25),
                 title, font_size=10, bold=True, color=accent_color, font_name="Segoe UI Semibold")

def create_lean_canvas():
    prs = Presentation()
    # Widescreen 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # ─── Background ───
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG
    
    # ─── Title Bar ───
    title_bar = add_rounded_rect(slide, Inches(0.3), Inches(0.2), Inches(12.73), Inches(0.65), RGBColor(0x1E, 0x29, 0x3B), CARD_BORDER)
    add_text_box(slide, Inches(0.5), Inches(0.25), Inches(4), Inches(0.55),
                 "🌉 SETU — Lean Canvas", font_size=20, bold=True, color=WHITE, font_name="Segoe UI Semibold")
    add_text_box(slide, Inches(5.0), Inches(0.28), Inches(3), Inches(0.25),
                 "Designed for: IBM SkillsBuild Internship", font_size=9, color=MID_GRAY)
    add_text_box(slide, Inches(8.0), Inches(0.28), Inches(2.5), Inches(0.25),
                 "Designed by: Abhinav Singh", font_size=9, color=MID_GRAY)
    add_text_box(slide, Inches(10.5), Inches(0.28), Inches(1.5), Inches(0.25),
                 "Date: July 2026", font_size=9, color=MID_GRAY)
    add_text_box(slide, Inches(12.0), Inches(0.28), Inches(1), Inches(0.25),
                 "Version: 1.0", font_size=9, bold=True, color=ACCENT_ORANGE)
    # Subtitle
    add_text_box(slide, Inches(0.5), Inches(0.52), Inches(8), Inches(0.25),
                 "AI Bridge to Rights, Schemes & Opportunities | Multi-Agent System | SDG 1, 4, 8, 10",
                 font_size=8, color=MID_GRAY)
    
    # ─── Grid Layout (5 columns, 3 rows) ───
    # Row 1: Problem | Solution | UVP | Unfair Advantage | Customer Segments
    # Row 2: Existing Alt | Key Metrics | High-Level Concept | Channels | Early Adopters
    # Row 3 (full width): Cost Structure | Revenue Streams
    
    margin = Inches(0.3)
    gap = Inches(0.12)
    grid_top = Inches(1.05)
    
    col_w = Inches(2.48)
    row1_h = Inches(2.55)
    row2_h = Inches(2.05)
    row3_h = Inches(1.4)
    
    cols = [margin + i * (col_w + gap) for i in range(5)]
    row2_top = grid_top + row1_h + gap
    row3_top = row2_top + row2_h + gap
    
    pad = Inches(0.12)
    text_pad = Inches(0.08)
    
    # ═══════════════════════════════════════════
    # ROW 1
    # ═══════════════════════════════════════════
    
    # ── 1. PROBLEM ──
    add_rounded_rect(slide, cols[0], grid_top, col_w, row1_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[0], grid_top, col_w, "🚨", "PROBLEM", ACCENT_RED)
    add_multiline_text(slide, cols[0] + pad, grid_top + Inches(0.35), col_w - 2*pad, row1_h - Inches(0.4), [
        "• 800M+ Indians eligible for welfare",
        "  schemes but 40% never claim benefits",
        "",
        "• Information scattered across 100+",
        "  portals in complex bureaucratic language",
        "",
        "• Rural citizens face language barriers",
        "  (Hindi/regional) and low digital literacy",
        "",
        "• No unified discovery tool; existing",
        "  portals require knowing the exact",
        "  scheme name to search",
        "",
        "• Zero verification — citizens can't tell",
        "  authentic info from misinformation",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 2. SOLUTION ──
    add_rounded_rect(slide, cols[1], grid_top, col_w, row1_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[1], grid_top, col_w, "💡", "SOLUTION", ACCENT_GREEN)
    add_multiline_text(slide, cols[1] + pad, grid_top + Inches(0.35), col_w - 2*pad, row1_h - Inches(0.4), [
        "• 5 Specialized AI Agents working in",
        "  pipeline: Language → Eligibility →",
        "  Verification → Opportunity → Planner",
        "",
        "• RAG pipeline with ChromaDB (98 chunks",
        "  from 18 verified government schemes)",
        "",
        "• Deterministic fact-verification using",
        "  confidence = 0.3×citation + 0.3×sim",
        "  + 0.4×coverage (not LLM hallucination)",
        "",
        "• Hindi + English conversational interface",
        "",
        "• Actionable step-by-step plans with",
        "  document checklists and portal links",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 3. UNIQUE VALUE PROPOSITION ──
    add_rounded_rect(slide, cols[2], grid_top, col_w, row1_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[2], grid_top, col_w, "⭐", "UNIQUE VALUE PROP.", ACCENT_ORANGE)
    add_multiline_text(slide, cols[2] + pad, grid_top + Inches(0.35), col_w - 2*pad, row1_h - Inches(0.4), [
        "\"Ask in your language. Get verified",
        "  schemes. Act with a plan.\"",
        "",
        "• Only tool that VERIFIES every claim",
        "  with deterministic scoring — not blind",
        "  LLM trust. Each response carries a",
        "  confidence badge (✅/⚠️/❌).",
        "",
        "• Covers scholarships, pensions, farming",
        "  subsidies, women's schemes, skill",
        "  training, and job portals in one chat.",
        "",
        "• Designed for low-literacy users —",
        "  speak naturally, get actionable plans",
        "  with document checklists.",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 4. UNFAIR ADVANTAGE ──
    add_rounded_rect(slide, cols[3], grid_top, col_w, row1_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[3], grid_top, col_w, "🛡️", "UNFAIR ADVANTAGE", ACCENT_BLUE)
    add_multiline_text(slide, cols[3] + pad, grid_top + Inches(0.35), col_w - 2*pad, row1_h - Inches(0.4), [
        "• Deterministic verification formula",
        "  (0.3C + 0.3S + 0.4Cov) — cannot be",
        "  easily replicated by prompt engineering",
        "",
        "• Curated, verified scheme corpus (18",
        "  schemes, 98 chunks) with metadata",
        "  that generic chatbots don't possess",
        "",
        "• Multi-agent architecture (LangGraph)",
        "  with specialized roles — not a single",
        "  monolithic prompt",
        "",
        "• IBM Granite + Groq inference = zero",
        "  API cost for unlimited queries",
        "",
        "• SDG-aligned mission (1, 4, 8, 10)",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 5. CUSTOMER SEGMENTS ──
    add_rounded_rect(slide, cols[4], grid_top, col_w, row1_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[4], grid_top, col_w, "👥", "CUSTOMER SEGMENTS", ACCENT_PINK)
    add_multiline_text(slide, cols[4] + pad, grid_top + Inches(0.35), col_w - 2*pad, row1_h - Inches(0.4), [
        "• SC/ST/OBC/Minority students seeking",
        "  scholarships (Pre/Post Matric, NMMSS,",
        "  Central Sector, state-level schemes)",
        "",
        "• BPL families & widows eligible for",
        "  pension schemes (IGWPS, Palanhar)",
        "",
        "• Small/marginal farmers (PM-KISAN,",
        "  MGNREGA, subsidy schemes)",
        "",
        "• Parents of girl children (Sukanya",
        "  Samriddhi, Kali Bai/Devnarayan Scooty)",
        "",
        "• Rural youth seeking skill training",
        "  (PMKVY) and job placements (NCS)",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ═══════════════════════════════════════════
    # ROW 2
    # ═══════════════════════════════════════════
    
    # ── 6. EXISTING ALTERNATIVES ──
    add_rounded_rect(slide, cols[0], row2_top, col_w, row2_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[0], row2_top, col_w, "🔄", "EXISTING ALTERNATIVES", ACCENT_RED)
    add_multiline_text(slide, cols[0] + pad, row2_top + Inches(0.35), col_w - 2*pad, row2_h - Inches(0.4), [
        "• MyScheme.gov.in — keyword search,",
        "  no AI, requires knowing scheme names",
        "",
        "• ChatGPT/Gemini — generic, hallucinates",
        "  scheme details, no verification layer",
        "",
        "• CSC/Jan Seva Kendra — physical visit,",
        "  limited hours, dependent on operators",
        "",
        "• Manual Google search — fragmented",
        "  results across 100+ ministry portals",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 7. KEY METRICS ──
    add_rounded_rect(slide, cols[1], row2_top, col_w, row2_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[1], row2_top, col_w, "📊", "KEY METRICS", ACCENT_GREEN)
    add_multiline_text(slide, cols[1] + pad, row2_top + Inches(0.35), col_w - 2*pad, row2_h - Inches(0.4), [
        "• 18 verified schemes in database",
        "• 98 document chunks in vector store",
        "• 5/6 automated self-tests passing",
        "• Avg confidence score ≥ 0.7 on verified",
        "  queries (citation + similarity based)",
        "",
        "• Response time: <5s (Groq), <30s (local)",
        "• Hindi + English language coverage",
        "• 100% deterministic verification",
        "  (no probabilistic hallucination)",
        "• $0 infrastructure cost (Groq free tier)",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 8. HIGH-LEVEL CONCEPT ──
    add_rounded_rect(slide, cols[2], row2_top, col_w, row2_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[2], row2_top, col_w, "🎯", "HIGH-LEVEL CONCEPT", ACCENT_ORANGE)
    add_multiline_text(slide, cols[2] + pad, row2_top + Inches(0.35), col_w - 2*pad, row2_h - Inches(0.4), [
        "\"Google for Government Schemes\"",
        "  + Built-in Fact-Checker",
        "",
        "Think of it as:",
        "• ChatGPT's conversational ease",
        "  + Wikipedia's citation rigor",
        "  + MyScheme's domain knowledge",
        "  + A social worker's personalized advice",
        "",
        "Tech Stack: IBM Granite 3.3 | LangGraph",
        "  | ChromaDB | Streamlit | Groq API",
        "  | sentence-transformers",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 9. CHANNELS ──
    add_rounded_rect(slide, cols[3], row2_top, col_w, row2_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[3], row2_top, col_w, "📡", "CHANNELS", ACCENT_BLUE)
    add_multiline_text(slide, cols[3] + pad, row2_top + Inches(0.35), col_w - 2*pad, row2_h - Inches(0.4), [
        "• Web App (Streamlit Community Cloud)",
        "  — accessible from any browser/phone",
        "",
        "• GitHub Open Source Repository",
        "  github.com/AbhinavSingh722/setu-ai",
        "",
        "• WhatsApp Bot integration (roadmap)",
        "  — reaches 500M+ Indian users",
        "",
        "• CSC/Gram Panchayat kiosk deployment",
        "  (roadmap) — serves offline users",
        "",
        "• IBM SkillsBuild showcase & demo",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 10. EARLY ADOPTERS ──
    add_rounded_rect(slide, cols[4], row2_top, col_w, row2_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[4], row2_top, col_w, "🎯", "EARLY ADOPTERS", ACCENT_PINK)
    add_multiline_text(slide, cols[4] + pad, row2_top + Inches(0.35), col_w - 2*pad, row2_h - Inches(0.4), [
        "• College students from SC/ST/OBC",
        "  communities applying for Post-Matric",
        "  Scholarships (immediate high value)",
        "",
        "• NGO field workers who assist villagers",
        "  with scheme applications daily",
        "",
        "• Gram Panchayat IT operators serving",
        "  as scheme information intermediaries",
        "",
        "• First-generation learners navigating",
        "  government portals for the first time",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ═══════════════════════════════════════════
    # ROW 3 (Two wide columns)
    # ═══════════════════════════════════════════
    
    half_w = (5 * col_w + 4 * gap - gap) / 2
    
    # ── 11. COST STRUCTURE ──
    add_rounded_rect(slide, cols[0], row3_top, half_w, row3_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, cols[0], row3_top, half_w, "💰", "COST STRUCTURE", ACCENT_RED)
    add_multiline_text(slide, cols[0] + pad, row3_top + Inches(0.35), half_w - 2*pad, row3_h - Inches(0.4), [
        "• LLM Inference: $0 (Groq free tier — llama3-8b-8192, 14,400 req/day)  •  Local: $0 (Ollama + IBM Granite open-source)",
        "• Vector DB: $0 (ChromaDB open-source, embedded)  •  Hosting: $0 (Streamlit Community Cloud, free tier)",
        "• Domain Knowledge: $0 (Government scheme documents are public)  •  Embeddings: $0 (all-MiniLM-L6-v2, open-source)",
        "• Total Cost to Operate: $0/month — fully open-source stack with zero paid APIs",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ── 12. REVENUE STREAMS ──
    r3_col2 = cols[0] + half_w + gap
    add_rounded_rect(slide, r3_col2, row3_top, half_w, row3_h, CARD_BG, CARD_BORDER)
    add_header_with_icon(slide, r3_col2, row3_top, half_w, "📈", "REVENUE STREAMS / IMPACT", ACCENT_GREEN)
    add_multiline_text(slide, r3_col2 + pad, row3_top + Inches(0.35), half_w - 2*pad, row3_h - Inches(0.4), [
        "• Social Impact Model — free for all citizens (SDG 1: No Poverty, SDG 4: Quality Education, SDG 8: Decent Work, SDG 10: Reduced Inequalities)",
        "• B2G (Business-to-Government): License to state govts for district-level deployment on CSC kiosks",
        "• NGO Partnerships: White-label for organizations like Pratham, Akshaya Patra who serve beneficiaries at scale",
        "• Future: Premium API for fintech/edtech platforms integrating scheme discovery into their apps",
    ], font_size=8, color=LIGHT_GRAY)
    
    # ─── Footer ───
    add_text_box(slide, Inches(0.3), Inches(7.15), Inches(12.73), Inches(0.3),
                 "🌉 SETU v1.0 — Built with IBM Granite 3.3 • LangGraph • ChromaDB • Groq API • Streamlit  |  github.com/AbhinavSingh722/setu-ai  |  IBM SkillsBuild AI Internship 2026",
                 font_size=7, color=MID_GRAY, alignment=PP_ALIGN.CENTER)
    
    # ─── Save ───
    prs.save(OUTPUT_PATH)
    print(f"✅ Lean Canvas saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    create_lean_canvas()
