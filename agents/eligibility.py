"""
SETU Eligibility & Scheme Agent

RAG-grounded agent that queries the ChromaDB scheme corpus and uses
IBM Granite (via Ollama) to identify schemes a user may be eligible for.

Key constraints (from spec §3):
- MUST use RAG retrieval — never answer from parametric memory alone
- Returns candidate schemes with EXACT source citations
- If no relevant chunks found, says so honestly — never fabricates
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingestion.chroma_store import SetuVectorStore, RetrievalResult


# --- Configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite3.3:8b")

ELIGIBILITY_SYSTEM_PROMPT = """You are the Eligibility & Scheme Agent for SETU, an AI system that helps Indian citizens find government welfare schemes and scholarships they are eligible for.

YOUR ROLE:
- Analyze the user's situation and match them with relevant government schemes
- ONLY recommend schemes that appear in the RETRIEVED CONTEXT below
- NEVER fabricate or hallucinate scheme names, amounts, eligibility criteria, or deadlines
- If the retrieved context does not contain relevant schemes, say so honestly

RULES:
1. Every scheme you mention MUST have a citation from the retrieved context
2. Include the exact scheme name as it appears in the source
3. Mention specific eligibility criteria, benefits/amounts, and required documents from the source
4. If a user's situation is unclear, note what additional information would help
5. Respond in the same language the user used (Hindi or English)
6. Keep your response focused and actionable

OUTPUT FORMAT:
For each recommended scheme, provide:
- Scheme Name (exact, from source)
- Why the user may be eligible (cite specific criteria from source)
- Key Benefits (exact amounts/details from source)
- Required Documents (from source)
- Source URL

If NO schemes match, state: "Based on the available scheme database, I could not find matching schemes for your situation. [explain why]"
"""


@dataclass
class SchemeRecommendation:
    """A single scheme recommendation with citation."""
    scheme_name: str
    eligibility_match: str  # Why user may be eligible
    benefits: str
    documents_required: str
    source_url: str
    source_section: str
    similarity_score: float
    raw_citations: list = field(default_factory=list)


@dataclass
class EligibilityResult:
    """Full result from the Eligibility agent."""
    query: str
    response_text: str  # Full LLM response
    recommendations: list  # List of scheme names found
    retrieved_chunks: list  # RetrievalResults used
    num_schemes_found: int
    agent_name: str = "Eligibility & Scheme Agent"
    status: str = "completed"  # completed, no_results, error


class EligibilityAgent:
    """
    RAG-grounded Eligibility agent.
    
    Flow:
    1. Receive user query/intent
    2. Query ChromaDB for relevant scheme chunks
    3. Construct prompt with retrieved context for Granite
    4. Return response with citations
    """
    
    def __init__(
        self,
        vector_store: Optional[SetuVectorStore] = None,
        model_name: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        n_results: int = 10,
    ):
        self.n_results = n_results
        
        # Initialize vector store
        if vector_store:
            self.store = vector_store
        else:
            self.store = SetuVectorStore()
        
        # Initialize Granite LLM via Ollama
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.1,  # Low temperature for factual accuracy
            num_predict=1024,
        )
    
    def retrieve_context(self, query: str, n_results: int = None) -> list[RetrievalResult]:
        """Retrieve relevant chunks from ChromaDB."""
        n = n_results or self.n_results
        results = self.store.query(query_text=query, n_results=n)
        return results
    
    def _format_context(self, chunks: list[RetrievalResult]) -> str:
        """Format retrieved chunks as context for the LLM prompt."""
        if not chunks:
            return "NO RELEVANT SCHEMES FOUND IN DATABASE."
        
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(
                f"--- Source {i+1} ---\n"
                f"Scheme: {chunk.scheme_name}\n"
                f"Section: {chunk.section}\n"
                f"URL: {chunk.source_url}\n"
                f"Relevance Score: {chunk.similarity_score:.3f}\n"
                f"Content:\n{chunk.text}\n"
            )
        
        return "\n".join(context_parts)
    
    def run(self, query: str, user_context: dict = None) -> EligibilityResult:
        """
        Run the eligibility agent on a user query.
        
        Args:
            query: User's question or description of their situation
            user_context: Optional structured context from Language agent
                         (e.g., {"category": "SC", "state": "Rajasthan", "education": "12th pass"})
        
        Returns:
            EligibilityResult with response, citations, and retrieved chunks
        """
        # Step 1: Enhance query with user context if available
        enhanced_query = query
        if user_context:
            context_parts = [f"{k}: {v}" for k, v in user_context.items() if v]
            if context_parts:
                enhanced_query = f"{query}\n\nUser details: {', '.join(context_parts)}"
        
        # Step 2: Retrieve relevant chunks
        retrieved = self.retrieve_context(enhanced_query)
        
        if not retrieved:
            return EligibilityResult(
                query=query,
                response_text="I could not find any relevant schemes in the database for your query. Please provide more details about your situation — such as your caste category, income level, education, state, and what type of help you need.",
                recommendations=[],
                retrieved_chunks=[],
                num_schemes_found=0,
                status="no_results",
            )
        
        # Step 3: Format context and construct prompt
        context_text = self._format_context(retrieved)
        
        user_prompt = (
            f"RETRIEVED CONTEXT FROM SCHEME DATABASE:\n"
            f"{context_text}\n\n"
            f"USER QUERY:\n{query}\n"
        )
        
        if user_context:
            user_prompt += f"\nUSER DETAILS: {json.dumps(user_context, ensure_ascii=False)}\n"
        
        user_prompt += (
            "\nBased ONLY on the retrieved context above, identify which schemes "
            "this user may be eligible for. Cite specific eligibility criteria, "
            "benefits, and required documents from the sources. "
            "Do NOT mention any scheme that is not in the retrieved context."
        )
        
        # Step 4: Call Granite via Ollama
        messages = [
            SystemMessage(content=ELIGIBILITY_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        
        try:
            response = self.llm.invoke(messages)
            response_text = response.content
        except Exception as e:
            return EligibilityResult(
                query=query,
                response_text=f"Error connecting to Granite model: {str(e)}. Please ensure Ollama is running with granite3.3:8b.",
                recommendations=[],
                retrieved_chunks=retrieved,
                num_schemes_found=0,
                status="error",
            )
        
        # Step 5: Extract scheme names mentioned in response
        unique_schemes = set()
        for chunk in retrieved:
            if chunk.scheme_name.lower() in response_text.lower() or \
               any(word in response_text.lower() for word in chunk.scheme_name.lower().split()[:3]):
                unique_schemes.add(chunk.scheme_name)
        
        recommendations = sorted(unique_schemes)
        
        return EligibilityResult(
            query=query,
            response_text=response_text,
            recommendations=recommendations,
            retrieved_chunks=retrieved,
            num_schemes_found=len(recommendations),
            status="completed",
        )


if __name__ == "__main__":
    print("=" * 60)
    print("SETU Eligibility Agent — Test Run")
    print("=" * 60)
    
    agent = EligibilityAgent()
    
    # Test query
    query = "I am an SC student from Rajasthan, my family income is 2 lakh per year. I have passed 12th class with 65% marks. What scholarships can I get?"
    
    print(f"\nQuery: {query}")
    print("-" * 60)
    
    result = agent.run(
        query=query,
        user_context={
            "category": "SC",
            "state": "Rajasthan",
            "income": "2 lakh per year",
            "education": "12th pass, 65%",
        }
    )
    
    print(f"\nStatus: {result.status}")
    print(f"Schemes found: {result.num_schemes_found}")
    print(f"Recommendations: {result.recommendations}")
    print(f"\nFull Response:\n{result.response_text}")
    print(f"\nRetrieved chunks ({len(result.retrieved_chunks)}):")
    for chunk in result.retrieved_chunks[:5]:
        print(f"  - {chunk.scheme_name} [{chunk.section}] (sim: {chunk.similarity_score:.3f})")
