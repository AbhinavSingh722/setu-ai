"""
Generate SETU AI Lean Canvas — Classic Neos Chronos Template Style
Matches the user's screenshot: white background, olive headers, red icons, thin borders
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SETU_Lean_Canvas_Classic.pptx")

# Colors matching the Neos Chronos template
OLIVE       = RGBColor(0x6B, 0x6B, 0x37)  # Olive green headers
RED_ICON    = RGBColor(0xCC, 0x33, 0x33)  # Red accent icons
BLACK       = RGBColor(0x00, 0x00, 0x00)
DARK_TEXT   = RGBColor(0x33, 0x33, 0x33)
BODY_TEXT   = RGBColor(0x44, 0x44, 0x44)
LIGHT_TEXT  = RGBColor(0x66, 0x66, 0x66)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
BORDER      = RGBColor(0xAA, 0xAA, 0xAA)
LIGHT_BG    = RGBColor(0xF8, 0xF8, 0xF8)
FOOTER_GRAY = RGBColor(0x88, 0x88, 0x88)


def add_rect(slide, left, top, width, height, fill=None, border_color=BORDER, border_width=Pt(0.75)):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    shape.line.color.rgb = border_color
    shape.line.width = border_width
    return shape


def add_text(slide, left, top, width, height, text, size=8, bold=False, color=BODY_TEXT, align=PP_ALIGN.LEFT, font="Calibri"):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font
    p.alignment = align
    return tb


def add_body(slide, left, top, width, height, lines, size=7.5, color=BODY_TEXT):
    """Add multi-line bullet text."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_after = Pt(1.5)
        p.space_before = Pt(0.5)
    return tb


def add_section_header(slide, left, top, width, title, icon_char=""):
    """Olive header text with red icon — matching the template."""
    # Red icon (small, top-right area of the header)
    if icon_char:
        icon_tb = slide.shapes.add_textbox(left + width - Inches(0.3), top + Inches(0.02), Inches(0.25), Inches(0.22))
        itf = icon_tb.text_frame
        ip = itf.paragraphs[0]
        ip.text = icon_char
        ip.font.size = Pt(10)
        ip.font.color.rgb = RED_ICON
        ip.font.name = "Calibri"
        ip.alignment = PP_ALIGN.RIGHT

    # Header text
    add_text(slide, left + Inches(0.06), top + Inches(0.04), width - Inches(0.35), Inches(0.2),
             title, size=9, bold=True, color=OLIVE, font="Calibri")


def create_lean_canvas():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # White background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE

    # ═══════════════════════════════════════════
    # TITLE AREA
    # ═══════════════════════════════════════════
    add_text(slide, Inches(0.4), Inches(0.2), Inches(3.5), Inches(0.45),
             "The Lean Canvas", size=22, bold=True, color=BLACK, font="Calibri")

    # Header fields: Designed for / Designed by / Date / Version
    # Field boxes with thin borders
    fields = [
        (Inches(4.2), "Designed for:", "Digital Dynamo"),
        (Inches(6.8), "Designed by:", "Abhinav Singh"),
        (Inches(9.4), "Date:", "16/07/2026"),
        (Inches(11.5), "Version:", "1.0"),
    ]
    for x, label, value in fields:
        w = Inches(2.3) if x < Inches(10) else Inches(1.5)
        add_text(slide, x, Inches(0.15), w, Inches(0.15), label, size=6.5, color=LIGHT_TEXT, align=PP_ALIGN.CENTER)
        add_rect(slide, x, Inches(0.32), w, Inches(0.3), fill=WHITE, border_color=BORDER, border_width=Pt(0.5))
        add_text(slide, x, Inches(0.34), w, Inches(0.28), value, size=9, color=DARK_TEXT, align=PP_ALIGN.CENTER)

    # ═══════════════════════════════════════════
    # GRID LAYOUT
    # ═══════════════════════════════════════════
    grid_left = Inches(0.4)
    grid_top = Inches(0.85)
    total_w = Inches(12.53)
    gap = Inches(0.0)  # No gap — shared borders like the template

    col_w = total_w / 5
    row1_h = Inches(2.5)
    row2_h = Inches(2.1)
    row3_h = Inches(1.5)

    row2_top = grid_top + row1_h
    row3_top = row2_top + row2_h

    pad_x = Inches(0.08)
    pad_y = Inches(0.32)

    # ─── ROW 1 ───────────────────────────────

    # 1. PROBLEM
    c0 = grid_left
    add_rect(slide, c0, grid_top, col_w, row1_h)
    add_section_header(slide, c0, grid_top, col_w, "Problem", "🔒")
    add_body(slide, c0 + pad_x, grid_top + pad_y, col_w - 2*pad_x, row1_h - pad_y - Inches(0.05), [
        "• 800M+ Indians eligible for welfare",
        "  schemes but ~40% never claim benefits",
        "",
        "• Information scattered across 100+",
        "  govt portals in complex bureaucratic",
        "  language inaccessible to rural citizens",
        "",
        "• Language barriers — Hindi/regional",
        "  speakers can't navigate English portals",
        "",
        "• No unified AI discovery tool; existing",
        "  portals require knowing exact scheme",
        "  names to search",
        "",
        "• Zero verification — citizens can't",
        "  distinguish authentic info from",
        "  misinformation online",
    ])

    # 2. SOLUTION
    c1 = grid_left + col_w
    add_rect(slide, c1, grid_top, col_w, row1_h)
    add_section_header(slide, c1, grid_top, col_w, "Solution", "🔑")
    add_body(slide, c1 + pad_x, grid_top + pad_y, col_w - 2*pad_x, row1_h - pad_y - Inches(0.05), [
        "• 5 Specialized AI Agents in pipeline:",
        "  Language → Eligibility → Verification",
        "  → Opportunity → Planner",
        "",
        "• RAG pipeline with ChromaDB (98 chunks",
        "  from 18 verified government schemes)",
        "",
        "• Deterministic fact-verification:",
        "  confidence = 0.3×citation + 0.3×sim",
        "  + 0.4×coverage (not LLM hallucination)",
        "",
        "• Hindi + English conversational chat",
        "",
        "• Actionable step-by-step plans with",
        "  document checklists & portal links",
    ])

    # 3. UNIQUE VALUE PROPOSITION
    c2 = grid_left + 2 * col_w
    add_rect(slide, c2, grid_top, col_w, row1_h)
    add_section_header(slide, c2, grid_top, col_w, "Unique Value Prop.", "🏆")
    add_body(slide, c2 + pad_x, grid_top + pad_y, col_w - 2*pad_x, row1_h - pad_y - Inches(0.05), [
        "\"Ask in your language. Get verified",
        "  schemes. Act with a plan.\"",
        "",
        "• Only tool that VERIFIES every claim",
        "  with deterministic scoring — not blind",
        "  LLM trust. Each response carries a",
        "  confidence badge (✅ / ⚠️ / ❌).",
        "",
        "• Covers scholarships, pensions, farming",
        "  subsidies, women's schemes, skill",
        "  training & job portals — all in one chat",
        "",
        "• Designed for low-literacy users — speak",
        "  naturally, get plans with checklists",
    ])

    # 4. UNFAIR ADVANTAGE
    c3 = grid_left + 3 * col_w
    add_rect(slide, c3, grid_top, col_w, row1_h)
    add_section_header(slide, c3, grid_top, col_w, "Unfair Advantage", "🦅")
    add_body(slide, c3 + pad_x, grid_top + pad_y, col_w - 2*pad_x, row1_h - pad_y - Inches(0.05), [
        "• Deterministic verification formula",
        "  (0.3C + 0.3S + 0.4Cov) — cannot be",
        "  replicated by prompt engineering alone",
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
    ])

    # 5. CUSTOMER SEGMENTS
    c4 = grid_left + 4 * col_w
    add_rect(slide, c4, grid_top, col_w, row1_h)
    add_section_header(slide, c4, grid_top, col_w, "Customer Segments", "👥")
    add_body(slide, c4 + pad_x, grid_top + pad_y, col_w - 2*pad_x, row1_h - pad_y - Inches(0.05), [
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
    ])

    # ─── ROW 2 ───────────────────────────────

    # 6. EXISTING ALTERNATIVES
    add_rect(slide, c0, row2_top, col_w, row2_h)
    add_section_header(slide, c0, row2_top, col_w, "Existing Alternatives", "🔄")
    add_body(slide, c0 + pad_x, row2_top + pad_y, col_w - 2*pad_x, row2_h - pad_y - Inches(0.05), [
        "• MyScheme.gov.in — keyword search,",
        "  no AI, requires knowing scheme names",
        "",
        "• ChatGPT/Gemini — generic, hallucinates",
        "  scheme details, no verification layer",
        "",
        "• CSC/Jan Seva Kendra — physical visit",
        "  required, limited hours, operator bias",
        "",
        "• Manual Google search — fragmented",
        "  results across 100+ ministry portals",
    ])

    # 7. KEY METRICS
    add_rect(slide, c1, row2_top, col_w, row2_h)
    add_section_header(slide, c1, row2_top, col_w, "Key Metrics", "📊")
    add_body(slide, c1 + pad_x, row2_top + pad_y, col_w - 2*pad_x, row2_h - pad_y - Inches(0.05), [
        "• 18 verified schemes in database",
        "• 98 document chunks in vector store",
        "• 5/6 automated self-tests passing",
        "• Avg confidence ≥ 0.7 on verified queries",
        "",
        "• Response time: <5s (Groq), <30s (local)",
        "• Hindi + English language coverage",
        "• 100% deterministic verification",
        "  (no probabilistic hallucination)",
        "• $0 infrastructure cost (Groq free tier)",
    ])

    # 8. HIGH-LEVEL CONCEPT
    add_rect(slide, c2, row2_top, col_w, row2_h)
    add_section_header(slide, c2, row2_top, col_w, "High-Level Concept", "⭐")
    add_body(slide, c2 + pad_x, row2_top + pad_y, col_w - 2*pad_x, row2_h - pad_y - Inches(0.05), [
        "\"Google for Government Schemes\"",
        "  + Built-in Fact-Checker",
        "",
        "Think of it as:",
        "• ChatGPT's conversational ease",
        "  + Wikipedia's citation rigor",
        "  + MyScheme's domain knowledge",
        "  + A social worker's personalized advice",
        "",
        "Tech: IBM Granite 3.3 | LangGraph",
        "  | ChromaDB | Streamlit | Groq API",
        "  | sentence-transformers",
    ])

    # 9. CHANNELS
    add_rect(slide, c3, row2_top, col_w, row2_h)
    add_section_header(slide, c3, row2_top, col_w, "Channels", "📡")
    add_body(slide, c3 + pad_x, row2_top + pad_y, col_w - 2*pad_x, row2_h - pad_y - Inches(0.05), [
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
    ])

    # 10. EARLY ADOPTERS
    add_rect(slide, c4, row2_top, col_w, row2_h)
    add_section_header(slide, c4, row2_top, col_w, "Early Adopters", "🎯")
    add_body(slide, c4 + pad_x, row2_top + pad_y, col_w - 2*pad_x, row2_h - pad_y - Inches(0.05), [
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
    ])

    # ─── ROW 3 (Two wide boxes) ──────────────

    half_w = total_w / 2

    # 11. COST STRUCTURE
    add_rect(slide, c0, row3_top, half_w, row3_h)
    add_section_header(slide, c0, row3_top, half_w, "Cost Structure", "💰")
    add_body(slide, c0 + pad_x, row3_top + pad_y, half_w - 2*pad_x, row3_h - pad_y - Inches(0.05), [
        "• LLM Inference: $0 (Groq free tier — llama3-8b-8192, 14,400 req/day)",
        "• Local Alternative: $0 (Ollama + IBM Granite 3.3 open-source weights)",
        "• Vector Database: $0 (ChromaDB open-source, embedded mode)",
        "• Hosting: $0 (Streamlit Community Cloud free tier)",
        "• Domain Knowledge: $0 (Government scheme docs are public domain)",
        "• Embeddings: $0 (all-MiniLM-L6-v2 open-source model)",
        "• Total Cost to Operate: $0/month — fully open-source, zero paid APIs",
    ], size=7.5)

    # 12. REVENUE STREAMS
    add_rect(slide, c0 + half_w, row3_top, half_w, row3_h)
    add_section_header(slide, c0 + half_w, row3_top, half_w, "Revenue Streams", "📈")
    add_body(slide, c0 + half_w + pad_x, row3_top + pad_y, half_w - 2*pad_x, row3_h - pad_y - Inches(0.05), [
        "• Social Impact Model — free for all citizens (primary mission)",
        "  SDG 1: No Poverty | SDG 4: Quality Education | SDG 8: Decent Work | SDG 10: Reduced Inequalities",
        "• B2G (Business-to-Government): License to state govts for district-level CSC kiosk deployment",
        "• NGO Partnerships: White-label for orgs like Pratham, Akshaya Patra serving beneficiaries at scale",
        "• Future: Premium API for fintech/edtech platforms integrating scheme discovery into their products",
    ], size=7.5)

    # ─── FOOTER ──────────────────────────────
    add_text(slide, Inches(0.4), Inches(7.15), total_w, Inches(0.25),
             "Lean Canvas is adapted from The Business Model Canvas (www.businessmodelgeneration.com/canvas). "
             "SETU v1.0 — Built with IBM Granite 3.3 • LangGraph • ChromaDB • Groq API • Streamlit  |  "
             "github.com/AbhinavSingh722/setu-ai  |  IBM SkillsBuild AI Internship 2026",
             size=6, color=FOOTER_GRAY, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(OUTPUT_PATH)
    print(f"Lean Canvas (Classic) saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_lean_canvas()
