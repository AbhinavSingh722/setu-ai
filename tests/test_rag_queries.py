"""Quick test: verify RAG retrieval works for all new scheme categories."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ingestion.chroma_store import SetuVectorStore

s = SetuVectorStore()
print(f"ChromaDB: {s.get_collection_stats()['total_chunks']} chunks, {s.get_collection_stats()['unique_schemes']} schemes\n")

queries = [
    ("micro loan for small business", ["MUDRA", "Stand-Up"]),
    ("free ration for BPL family", ["NFSA", "Ration"]),
    ("pension for unorganized worker", ["Atal Pension", "APY"]),
    ("housing subsidy for poor", ["Awas"]),
    ("crop insurance farmer", ["Fasal Bima"]),
    ("LPG connection for women", ["Ujjwala"]),
    ("health insurance card", ["Ayushman", "Chiranjeevi"]),
    ("education loan Bihar student", ["Bihar Student Credit"]),
    ("artisan craftsman loan training", ["Vishwakarma"]),
    ("maternity benefit pregnant woman", ["Matru Vandana"]),
    ("girl child savings scheme UP", ["Kanya Sumangala", "Sukanya"]),
    ("monthly payment women MP", ["Ladli Behna"]),
]

passed = 0
for q, expected_keywords in queries:
    results = s.query(q, n_results=3)
    top_names = [r.scheme_name for r in results[:3]]
    matched = any(
        any(kw.lower() in name.lower() for kw in expected_keywords)
        for name in top_names
    )
    status = "OK" if matched else "MISS"
    if matched:
        passed += 1
    top = results[0].scheme_name if results else "NONE"
    sim = results[0].similarity_score if results else 0
    print(f"  [{status}] {q:40s} -> {top[:55]} ({sim:.3f})")

print(f"\nResult: {passed}/{len(queries)} queries matched expected schemes")

# Test PDF generation
print("\nTesting PDF generation...")
try:
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "SETU Test PDF", ln=True)
    output = pdf.output()
    print(f"  PDF generation: OK ({len(output)} bytes)")
except Exception as e:
    print(f"  PDF generation: FAILED ({e})")

print("\nAll tests complete!")
