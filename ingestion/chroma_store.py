"""
SETU ChromaDB Vector Store — Chunk Storage & Retrieval

Loads document chunks into ChromaDB with embeddings and metadata
for RAG-based retrieval by the Eligibility agent.

Design decisions:
- Uses ChromaDB's default embedding function (all-MiniLM-L6-v2) for simplicity
  and zero-config setup. Can be swapped for sentence-transformers if needed.
- Collection name: "setu_schemes" for scheme data, "setu_opportunities" for jobs
- Metadata includes source_url, scheme_name, section for citation tracing
- Provides query interface returning chunks with similarity scores
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import chromadb
from chromadb.config import Settings

# Import from sibling module
from ingestion.docling_pipeline import DocumentChunk, process_directory


# Default paths
DEFAULT_CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data")
DEFAULT_COLLECTION = "setu_schemes"


@dataclass
class RetrievalResult:
    """A single result from vector store query, with score."""
    text: str
    scheme_name: str
    source_url: str
    section: str
    retrieval_date: str
    similarity_score: float  # 0-1, higher is better (converted from distance)
    chunk_id: str
    file_path: str
    category: str = ""
    level: str = ""

    def citation_string(self) -> str:
        """Format as a human-readable citation."""
        return (
            f"[Source: {self.scheme_name} | Section: {self.section} | "
            f"URL: {self.source_url} | Confidence: {self.similarity_score:.2f}]"
        )


class SetuVectorStore:
    """
    ChromaDB-backed vector store for SETU scheme data.
    
    Provides:
    - Batch ingestion of DocumentChunks
    - Semantic search with similarity scores
    - Citation-aware retrieval
    """
    
    def __init__(
        self,
        persist_dir: str = DEFAULT_CHROMA_DIR,
        collection_name: str = DEFAULT_COLLECTION,
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Get or create collection (uses default embedding: all-MiniLM-L6-v2)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Cosine similarity
        )
    
    def ingest_chunks(self, chunks: list[DocumentChunk], batch_size: int = 50) -> int:
        """
        Add document chunks to the vector store.
        
        Returns the number of chunks successfully added.
        """
        if not chunks:
            return 0
        
        added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            ids = [c.chunk_id for c in batch]
            documents = [c.text for c in batch]
            metadatas = [c.to_dict() for c in batch]
            
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            added += len(batch)
            print(f"  Ingested batch {i // batch_size + 1}: {len(batch)} chunks")
        
        return added
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_scheme: Optional[str] = None,
        filter_section: Optional[str] = None,
    ) -> list[RetrievalResult]:
        """
        Query the vector store for relevant chunks.
        
        Args:
            query_text: The search query
            n_results: Maximum number of results to return
            filter_scheme: Optional scheme name filter
            filter_section: Optional section filter (e.g., "ELIGIBILITY")
            
        Returns:
            List of RetrievalResults sorted by relevance (highest first)
        """
        # Build where filter
        where_filter = None
        if filter_scheme and filter_section:
            where_filter = {
                "$and": [
                    {"scheme_name": {"$eq": filter_scheme}},
                    {"section": {"$eq": filter_section}},
                ]
            }
        elif filter_scheme:
            where_filter = {"scheme_name": {"$eq": filter_scheme}}
        elif filter_section:
            where_filter = {"section": {"$eq": filter_section}}
        
        # Query ChromaDB
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            print(f"Query error: {e}")
            return []
        
        # Convert to RetrievalResults
        retrieval_results = []
        if results and results["documents"] and results["documents"][0]:
            for idx, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )):
                # ChromaDB cosine distance → similarity score (0-1)
                # Cosine distance = 1 - cosine_similarity
                similarity = max(0.0, 1.0 - dist)
                
                retrieval_results.append(RetrievalResult(
                    text=doc,
                    scheme_name=meta.get("scheme_name", ""),
                    source_url=meta.get("source_url", ""),
                    section=meta.get("section", ""),
                    retrieval_date=meta.get("retrieval_date", ""),
                    similarity_score=similarity,
                    chunk_id=meta.get("chunk_id", ""),
                    file_path=meta.get("file_path", ""),
                    category=meta.get("category", ""),
                    level=meta.get("level", ""),
                ))
        
        return retrieval_results
    
    def get_all_scheme_names(self) -> list[str]:
        """Return all unique scheme names in the store."""
        results = self.collection.get(include=["metadatas"])
        if results and results["metadatas"]:
            return sorted(set(m.get("scheme_name", "") for m in results["metadatas"]))
        return []
    
    def get_collection_stats(self) -> dict:
        """Return basic stats about the collection."""
        count = self.collection.count()
        schemes = self.get_all_scheme_names()
        return {
            "total_chunks": count,
            "unique_schemes": len(schemes),
            "scheme_names": schemes,
            "collection_name": self.collection_name,
            "persist_dir": self.persist_dir,
        }
    
    def clear(self):
        """Delete and recreate the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )


def build_vector_store(
    data_dir: str = None,
    persist_dir: str = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION,
    clear_existing: bool = True,
) -> SetuVectorStore:
    """
    Full pipeline: parse documents → chunk → embed → store in ChromaDB.
    
    Args:
        data_dir: Directory containing scheme documents
        persist_dir: Where to persist ChromaDB data
        collection_name: ChromaDB collection name
        clear_existing: If True, clear existing data before ingesting
        
    Returns:
        Initialized and populated SetuVectorStore
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    print("=" * 60)
    print("SETU Vector Store — Building from documents")
    print("=" * 60)
    print(f"  Data directory: {data_dir}")
    print(f"  ChromaDB path: {persist_dir}")
    print(f"  Collection: {collection_name}")
    print()
    
    # Step 1: Parse and chunk documents
    print("Step 1: Parsing and chunking documents...")
    all_chunks = process_directory(data_dir)
    print()
    
    # Step 2: Initialize vector store
    print("Step 2: Initializing ChromaDB...")
    store = SetuVectorStore(persist_dir, collection_name)
    
    if clear_existing:
        print("  Clearing existing data...")
        store.clear()
    
    # Step 3: Ingest chunks
    print("\nStep 3: Ingesting chunks into ChromaDB...")
    added = store.ingest_chunks(all_chunks)
    
    # Step 4: Print stats
    print(f"\n{'=' * 60}")
    stats = store.get_collection_stats()
    print(f"Build complete!")
    print(f"  Total chunks stored: {stats['total_chunks']}")
    print(f"  Unique schemes: {stats['unique_schemes']}")
    print(f"  Schemes: {', '.join(stats['scheme_names'][:5])}{'...' if len(stats['scheme_names']) > 5 else ''}")
    
    return store


if __name__ == "__main__":
    import sys
    
    # Build the vector store
    store = build_vector_store(clear_existing=True)
    
    # Run a test query
    print(f"\n{'=' * 60}")
    print("Test Query: 'SC student scholarship post matric eligibility'")
    print("=" * 60)
    
    results = store.query("SC student scholarship post matric eligibility", n_results=3)
    for i, r in enumerate(results):
        print(f"\n--- Result {i + 1} ---")
        print(f"  Scheme: {r.scheme_name}")
        print(f"  Section: {r.section}")
        print(f"  Similarity: {r.similarity_score:.3f}")
        print(f"  Citation: {r.citation_string()}")
        print(f"  Text (first 200 chars): {r.text[:200]}...")
