"""Final verification of all enhancements."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 1. Check app.py compiles
import py_compile
py_compile.compile('ui/app.py', doraise=True)
print("[OK] ui/app.py compiles cleanly")

py_compile.compile('agents/orchestrator.py', doraise=True)
print("[OK] agents/orchestrator.py compiles cleanly")

# 2. Count lines and features
with open('ui/app.py', 'r', encoding='utf-8') as f:
    source = f.read()
    lines = source.count('\n') + 1
    pages = source.count('elif page ==') + 1  # +1 for the first if
    print(f"[OK] app.py: {lines} lines, {pages} pages")

# 3. Verify new pages exist
assert 'Document Checklist' in source, "Missing Document Checklist page"
assert 'Deadlines' in source, "Missing Deadlines page"
print("[OK] New pages: Document Checklist, Deadlines")

# 4. Verify new features
assert 'generate_chat_pdf' in source, "Missing PDF export"
assert 'generate_checklist_pdf' in source, "Missing Checklist PDF"
assert 'format_response_with_cards' in source, "Missing rich card formatting"
assert 'resolve_references' in source, "Missing multi-turn reference resolver"
assert 'dark_mode' in source, "Missing dark mode"
assert 'SUCCESS_STORIES' in source, "Missing success stories"
assert 'HELPLINES' in source, "Missing helplines"
assert 'feedback' in source, "Missing feedback system"
print("[OK] All new features present: PDF export, checklist, rich cards, multi-turn, dark mode, stories, helplines, feedback")

# 5. Count schemes in SCHEME_DB
scheme_count = source.count('"name":')
# More accurate count
import re
scheme_entries = re.findall(r'\{"name":\s*"[^"]+",\s*"cat":', source)
print(f"[OK] SCHEME_DB entries: {len(scheme_entries)}")

# 6. Verify ChromaDB
from ingestion.chroma_store import SetuVectorStore
s = SetuVectorStore()
stats = s.get_collection_stats()
print(f"[OK] ChromaDB: {stats['total_chunks']} chunks, {stats['unique_schemes']} schemes")

# 7. Verify orchestrator update
with open('agents/orchestrator.py', 'r') as f:
    orc = f.read()
assert 'conversation_history' in orc, "orchestrator missing conversation_history param"
assert 'user_profile' in orc, "orchestrator missing user_profile param"
print("[OK] Orchestrator supports multi-turn context")

# 8. Verify requirements
with open('requirements.txt', 'r') as f:
    reqs = f.read()
assert 'fpdf2' in reqs, "Missing fpdf2 in requirements"
print("[OK] requirements.txt includes fpdf2")

# 9. Verify data files
data_dir = 'data/schemes'
scheme_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
print(f"[OK] Data files: {len(scheme_files)} scheme documents")

# 10. Verify PDF generation
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "", 12)
pdf.cell(0, 10, "SETU Test", new_x="LMARGIN", new_y="NEXT")
output = pdf.output()
assert len(output) > 100, "PDF too small"
print(f"[OK] PDF generation works ({len(output)} bytes)")

print("\n" + "=" * 60)
print("ALL VERIFICATIONS PASSED!")
print("=" * 60)
