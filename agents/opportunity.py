"""
SETU Opportunity Agent

Searches opportunity data (PMKVY skill courses, NCS job portal) to recommend
livelihood-related opportunities beyond just welfare schemes.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from langchain_ollama import ChatOllama
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None
from langchain_core.messages import HumanMessage, SystemMessage

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingestion.chroma_store import SetuVectorStore, RetrievalResult


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite3.3:8b")

OPPORTUNITY_SYSTEM_PROMPT = """You are the Opportunity Agent for SETU. Your job is to recommend livelihood opportunities — skill training, job portals, apprenticeships — to the user based on their situation.

RULES:
1. ONLY recommend opportunities from the RETRIEVED CONTEXT below
2. Focus on practical, actionable opportunities the user can pursue
3. Include registration steps and portal links from the source
4. If no relevant opportunities exist in the context, say so honestly
5. Respond in the same language the user used (Hindi or English)

For each opportunity, provide:
- Name and type (skill training, job portal, etc.)
- How it's relevant to the user
- How to register/apply
- Source URL
"""


@dataclass
class OpportunityResult:
    """Result from the Opportunity agent."""
    query: str
    response_text: str
    opportunities_found: list
    retrieved_chunks: list
    agent_name: str = "Opportunity Agent"
    status: str = "completed"


class OpportunityAgent:
    """Searches opportunity corpus for relevant livelihood options."""
    
    def __init__(
        self,
        vector_store: Optional[SetuVectorStore] = None,
        model_name: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL,
    ):
        self.store = vector_store or SetuVectorStore()
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key and ChatGroq:
            self.llm = ChatGroq(
                model="llama3-8b-8192",
                api_key=groq_api_key,
                temperature=0.1,
                max_tokens=512,
            )
        else:
            self.llm = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.1,
                num_predict=512,
            )
    
    def run(self, query: str, user_profile: dict = None) -> OpportunityResult:
        """Search for relevant opportunities."""
        # Enhance query for opportunity-specific retrieval
        opp_query = f"skill training job employment opportunity {query}"
        if user_profile:
            if user_profile.get("education"):
                opp_query += f" education {user_profile['education']}"
            if user_profile.get("age"):
                opp_query += f" age {user_profile['age']}"
        
        retrieved = self.store.query(query_text=opp_query, n_results=6)
        
        # Filter to opportunity-type results
        opp_chunks = [r for r in retrieved if any(
            kw in r.scheme_name.lower()
            for kw in ["pmkvy", "kaushal", "career", "ncs", "skill"]
        )]
        
        if not opp_chunks:
            opp_chunks = retrieved[:3]  # Fallback to top results
        
        if not opp_chunks:
            return OpportunityResult(
                query=query,
                response_text="No relevant opportunities found in the database.",
                opportunities_found=[],
                retrieved_chunks=[],
                status="no_results",
            )
        
        # Format context
        context_parts = []
        for i, chunk in enumerate(opp_chunks):
            context_parts.append(
                f"--- Source {i+1} ---\n"
                f"Program: {chunk.scheme_name}\nSection: {chunk.section}\n"
                f"URL: {chunk.source_url}\nContent:\n{chunk.text}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        prompt = (
            f"RETRIEVED CONTEXT:\n{context_text}\n\n"
            f"USER QUERY: {query}\n\n"
            f"Based ONLY on the context above, recommend relevant livelihood opportunities."
        )
        
        try:
            messages = [
                SystemMessage(content=OPPORTUNITY_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            response_text = response.content
        except Exception as e:
            response_text = f"Error: {str(e)}"
        
        # Extract opportunity names
        opps = list(set(c.scheme_name for c in opp_chunks))
        
        return OpportunityResult(
            query=query,
            response_text=response_text,
            opportunities_found=opps,
            retrieved_chunks=opp_chunks,
        )


if __name__ == "__main__":
    agent = OpportunityAgent()
    result = agent.run("I want to learn computer skills and get a job")
    print(f"Opportunities: {result.opportunities_found}")
    print(f"Response: {result.response_text[:500]}")
