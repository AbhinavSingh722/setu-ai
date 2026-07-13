"""
SETU Ingestion Pipeline — Document Parser & Chunker

Converts scheme/opportunity documents into structured, citable text chunks
for loading into ChromaDB. Supports both structured text files and PDFs.

Design decisions:
- Text files are parsed using a custom structured parser (our scheme docs)
- PDF files use pdfplumber (Docling fallback documented in PROGRESS.md)
- Chunks are ~500 tokens with metadata for citation traceability
- Every chunk carries: source_url, scheme_name, retrieval_date, chunk_id, section
"""

import os
import re
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class DocumentChunk:
    """A single citable chunk from a scheme document."""
    chunk_id: str
    text: str
    scheme_name: str
    source_url: str
    retrieval_date: str
    section: str  # e.g. "ELIGIBILITY", "BENEFITS", "APPLICATION_PROCESS"
    chunk_index: int
    total_chunks: int
    file_path: str
    category: str = ""
    level: str = ""  # "Central Government" or "State Government (Rajasthan)"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dict for ChromaDB metadata storage."""
        return {
            "chunk_id": self.chunk_id,
            "scheme_name": self.scheme_name,
            "source_url": self.source_url,
            "retrieval_date": self.retrieval_date,
            "section": self.section,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "file_path": self.file_path,
            "category": self.category,
            "level": self.level,
        }


def _generate_chunk_id(file_path: str, chunk_index: int) -> str:
    """Generate a deterministic chunk ID from file path and index."""
    raw = f"{file_path}::chunk_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _extract_field(text: str, field_name: str) -> str:
    """Extract a field value from structured text (FIELD_NAME: value format)."""
    pattern = rf"^{re.escape(field_name)}:\s*(.+?)$"
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_section(text: str, section_name: str) -> str:
    """Extract a full section from structured text (SECTION_NAME:\\n content)."""
    # Try to find section that starts with the name and ends at the next section or end
    pattern = rf"^{re.escape(section_name)}:\s*\n(.*?)(?=\n[A-Z][A-Z _/&()]+:|$)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Also try single-line format
    pattern = rf"^{re.escape(section_name)}:\s*(.+?)$"
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_structured_text(file_path: str) -> dict:
    """
    Parse a structured scheme text file into sections.
    
    Returns a dict with keys: scheme_name, scheme_name_hindi, source_url,
    category, level, and section content blocks.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    result = {
        "scheme_name": _extract_field(text, "SCHEME NAME"),
        "scheme_name_hindi": _extract_field(text, "SCHEME NAME (HINDI)"),
        "source_url": _extract_field(text, "SOURCE URL"),
        "official_portal": _extract_field(text, "OFFICIAL PORTAL"),
        "category": _extract_field(text, "CATEGORY"),
        "level": _extract_field(text, "LEVEL"),
        "implementing_ministry": (
            _extract_field(text, "IMPLEMENTING MINISTRY") or 
            _extract_field(text, "IMPLEMENTING DEPARTMENT") or
            _extract_field(text, "IMPLEMENTING AGENCY")
        ),
        "retrieval_date": _extract_field(text, "RETRIEVAL DATE"),
        "raw_text": text,
    }
    
    # Extract major content sections
    sections_to_extract = [
        "OBJECTIVE",
        "ELIGIBILITY CRITERIA",
        "ELIGIBILITY",
        "BENEFITS",
        "FINANCIAL BENEFITS",
        "KEY FEATURES FOR JOB SEEKERS",
        "SERVICES PROVIDED",
        "DOCUMENTS REQUIRED",
        "MANDATORY ANNUAL REQUIREMENT",
        "APPLICATION PROCESS",
        "REGISTRATION PROCESS",
        "SELECTION PROCESS",
        "RENEWAL CRITERIA",
        "COURSES AVAILABLE",
        "EXAMS COVERED",
        "HELP DESK",
        "SPECIAL FEATURES",
        "CURRENT PHASE",
        "SCHOLARSHIP AMOUNT",
    ]
    
    sections = {}
    for section_name in sections_to_extract:
        content = _extract_section(text, section_name)
        if content:
            sections[section_name] = content
    
    result["sections"] = sections
    return result


def chunk_document(parsed: dict, file_path: str, max_chunk_size: int = 500) -> list[DocumentChunk]:
    """
    Convert a parsed document into citable chunks.
    
    Strategy:
    1. Create a header chunk with scheme overview (name, category, objective)
    2. Create one chunk per major section (eligibility, benefits, etc.)
    3. If a section exceeds max_chunk_size words, split into sub-chunks with overlap
    """
    chunks = []
    scheme_name = parsed["scheme_name"]
    source_url = parsed["source_url"]
    retrieval_date = parsed.get("retrieval_date", "")
    category = parsed.get("category", "")
    level = parsed.get("level", "")
    
    # --- Chunk 0: Scheme Overview ---
    overview_parts = [
        f"Scheme: {scheme_name}",
    ]
    if parsed.get("scheme_name_hindi"):
        overview_parts.append(f"Hindi Name: {parsed['scheme_name_hindi']}")
    if category:
        overview_parts.append(f"Category: {category}")
    if level:
        overview_parts.append(f"Level: {level}")
    if parsed.get("implementing_ministry"):
        overview_parts.append(f"Implementing Body: {parsed['implementing_ministry']}")
    if parsed.get("official_portal"):
        overview_parts.append(f"Official Portal: {parsed['official_portal']}")
    
    objective = parsed["sections"].get("OBJECTIVE", "")
    if objective:
        overview_parts.append(f"\nObjective: {objective}")
    
    overview_text = "\n".join(overview_parts)
    chunks.append(DocumentChunk(
        chunk_id=_generate_chunk_id(file_path, 0),
        text=overview_text,
        scheme_name=scheme_name,
        source_url=source_url,
        retrieval_date=retrieval_date,
        section="OVERVIEW",
        chunk_index=0,
        total_chunks=0,  # Will be updated after all chunks created
        file_path=file_path,
        category=category,
        level=level,
    ))
    
    # --- Section chunks ---
    for section_name, section_content in parsed["sections"].items():
        if section_name == "OBJECTIVE":
            continue  # Already in overview
        
        section_text = f"Scheme: {scheme_name}\nSection: {section_name}\n\n{section_content}"
        
        words = section_text.split()
        if len(words) <= max_chunk_size:
            # Single chunk for this section
            chunks.append(DocumentChunk(
                chunk_id=_generate_chunk_id(file_path, len(chunks)),
                text=section_text,
                scheme_name=scheme_name,
                source_url=source_url,
                retrieval_date=retrieval_date,
                section=section_name,
                chunk_index=len(chunks),
                total_chunks=0,
                file_path=file_path,
                category=category,
                level=level,
            ))
        else:
            # Split large section into overlapping sub-chunks
            overlap = 50  # words of overlap between chunks
            start = 0
            sub_idx = 0
            while start < len(words):
                end = min(start + max_chunk_size, len(words))
                chunk_words = words[start:end]
                
                # Add section context header to sub-chunks after the first
                if sub_idx > 0:
                    prefix = f"Scheme: {scheme_name}\nSection: {section_name} (continued)\n\n"
                    chunk_text = prefix + " ".join(chunk_words)
                else:
                    chunk_text = " ".join(chunk_words)
                
                chunks.append(DocumentChunk(
                    chunk_id=_generate_chunk_id(file_path, len(chunks)),
                    text=chunk_text,
                    scheme_name=scheme_name,
                    source_url=source_url,
                    retrieval_date=retrieval_date,
                    section=f"{section_name}_part{sub_idx + 1}",
                    chunk_index=len(chunks),
                    total_chunks=0,
                    file_path=file_path,
                    category=category,
                    level=level,
                ))
                
                start = end - overlap if end < len(words) else end
                sub_idx += 1
    
    # Update total_chunks count
    for chunk in chunks:
        chunk.total_chunks = len(chunks)
    
    return chunks


def parse_pdf_document(file_path: str) -> dict:
    """
    Parse a PDF document into sections using pdfplumber.
    
    Falls back from Docling to pdfplumber for Windows compatibility.
    See PROGRESS.md for deviation log.
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber is required for PDF processing. Install: pip install pdfplumber")
    
    text_pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    
    full_text = "\n\n".join(text_pages)
    
    # For PDFs, we create a simpler structure
    return {
        "scheme_name": Path(file_path).stem.replace("_", " ").title(),
        "scheme_name_hindi": "",
        "source_url": "",
        "official_portal": "",
        "category": "",
        "level": "",
        "implementing_ministry": "",
        "retrieval_date": "",
        "raw_text": full_text,
        "sections": {"FULL_DOCUMENT": full_text},
    }


def process_directory(
    data_dir: str,
    max_chunk_size: int = 500,
) -> list[DocumentChunk]:
    """
    Process all documents in a directory (and subdirectories).
    Supports .txt (structured) and .pdf files.
    
    Returns list of all DocumentChunks ready for ChromaDB ingestion.
    """
    all_chunks = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Process all supported files
    for file_path in sorted(data_path.rglob("*")):
        if file_path.suffix.lower() == ".txt":
            print(f"  Parsing: {file_path.name}")
            parsed = parse_structured_text(str(file_path))
            chunks = chunk_document(parsed, str(file_path), max_chunk_size)
            all_chunks.extend(chunks)
            print(f"    -> {len(chunks)} chunks created")
        elif file_path.suffix.lower() == ".pdf":
            print(f"  Parsing PDF: {file_path.name}")
            parsed = parse_pdf_document(str(file_path))
            chunks = chunk_document(parsed, str(file_path), max_chunk_size)
            all_chunks.extend(chunks)
            print(f"    -> {len(chunks)} chunks created")
    
    print(f"\nTotal: {len(all_chunks)} chunks from {data_path}")
    return all_chunks


if __name__ == "__main__":
    # Quick test: process all data and show stats
    import sys
    
    base_dir = Path(__file__).parent.parent / "data"
    
    print("=" * 60)
    print("SETU Ingestion Pipeline — Document Processing")
    print("=" * 60)
    
    all_chunks = process_directory(str(base_dir))
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Total chunks: {len(all_chunks)}")
    
    # Show unique schemes
    schemes = set(c.scheme_name for c in all_chunks)
    print(f"  Unique schemes: {len(schemes)}")
    for s in sorted(schemes):
        scheme_chunks = [c for c in all_chunks if c.scheme_name == s]
        print(f"    - {s}: {len(scheme_chunks)} chunks")
    
    # Show one example chunk
    if all_chunks:
        print(f"\n{'=' * 60}")
        print("Example chunk (first eligibility chunk found):")
        print("=" * 60)
        for chunk in all_chunks:
            if "ELIGIBILITY" in chunk.section:
                print(f"  Chunk ID: {chunk.chunk_id}")
                print(f"  Scheme: {chunk.scheme_name}")
                print(f"  Section: {chunk.section}")
                print(f"  Source: {chunk.source_url}")
                print(f"  Text preview (first 300 chars):")
                print(f"    {chunk.text[:300]}...")
                break
