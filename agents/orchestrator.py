"""
SETU LangGraph Orchestrator

Central coordinator that routes user queries through the multi-agent pipeline:

    User Input -> Language Agent -> Eligibility Agent -> Verification Agent
                                 -> Opportunity Agent  -> Planner Agent
                                                                    -> Response

Uses LangGraph for state management and conditional routing.
The graph has real conditional edges — not a fixed linear pipeline.

Routing logic:
- All queries go through Language Agent first
- "find_schemes" / "check_eligibility" -> Eligibility + Verification + Planner
- "find_opportunities" -> Opportunity + Planner
- Combined queries -> all agents
"""

import os
import sys
from dataclasses import dataclass, field
from typing import TypedDict, Annotated, Optional

from langgraph.graph import StateGraph, END

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingestion.chroma_store import SetuVectorStore
from agents.language import LanguageAgent, IntakeResult
from agents.eligibility import EligibilityAgent, EligibilityResult
from agents.verification import VerificationAgent, VerificationResult
from agents.opportunity import OpportunityAgent, OpportunityResult
from agents.planner import PlannerAgent, PlannerResult


# --- State Definition ---
class SetuState(TypedDict):
    """Shared state passed between agents in the graph."""
    # Input
    user_message: str
    
    # Language Agent output
    intake: Optional[dict]
    detected_language: str
    intent: str
    user_profile: dict
    query_en: str
    
    # Eligibility Agent output
    eligibility: Optional[dict]
    eligible_schemes: list
    
    # Verification Agent output
    verification: Optional[dict]
    verification_summary: str
    overall_confidence: float
    
    # Opportunity Agent output
    opportunity: Optional[dict]
    
    # Planner Agent output
    plan: Optional[dict]
    
    # Final output
    final_response: str
    agent_trace: list  # Ordered list of agent names + summaries for transparency


# --- Node Functions ---

def language_node(state: SetuState) -> dict:
    """Run Language & Intake agent."""
    agent = LanguageAgent()
    result = agent.run(state["user_message"])
    
    return {
        "intake": {
            "detected_language": result.detected_language,
            "intent": result.intent,
            "user_profile": result.user_profile,
            "query_summary_en": result.query_summary_en,
            "status": result.status,
        },
        "detected_language": result.detected_language,
        "intent": result.intent,
        "user_profile": result.user_profile or {},
        "query_en": result.query_summary_en,
        "agent_trace": state.get("agent_trace", []) + [
            f"[Language Agent] Detected: {result.detected_language}, Intent: {result.intent}"
        ],
    }


def eligibility_node(state: SetuState) -> dict:
    """Run Eligibility & Scheme agent with RAG retrieval."""
    store = SetuVectorStore()
    agent = EligibilityAgent(vector_store=store)
    
    result = agent.run(
        query=state.get("query_en", state["user_message"]),
        user_context=state.get("user_profile", {}),
    )
    
    return {
        "eligibility": {
            "response_text": result.response_text,
            "recommendations": result.recommendations,
            "num_schemes": result.num_schemes_found,
            "status": result.status,
            "retrieved_chunks": [
                {
                    "scheme": c.scheme_name,
                    "section": c.section,
                    "similarity": c.similarity_score,
                    "source_url": c.source_url,
                }
                for c in result.retrieved_chunks[:5]
            ],
        },
        "eligible_schemes": result.recommendations,
        "agent_trace": state.get("agent_trace", []) + [
            f"[Eligibility Agent] Found {result.num_schemes_found} schemes: {', '.join(result.recommendations[:3])}"
        ],
    }


def verification_node(state: SetuState) -> dict:
    """Run Verification & Grounding agent."""
    store = SetuVectorStore()
    agent = VerificationAgent(vector_store=store)
    
    # Build a minimal EligibilityResult for verification
    elig_data = state.get("eligibility", {})
    
    elig_result = EligibilityResult(
        query=state.get("query_en", ""),
        response_text=elig_data.get("response_text", ""),
        recommendations=elig_data.get("recommendations", []),
        retrieved_chunks=[],
        num_schemes_found=elig_data.get("num_schemes", 0),
    )
    
    result = agent.verify_eligibility_result(elig_result)
    
    # Format verification summary
    summary_parts = []
    for v in result.claim_verifications:
        icon = {"VERIFIED": "[OK]", "NEEDS_REVIEW": "[!!]", "UNVERIFIED": "[XX]"}.get(v.verdict, "??")
        summary_parts.append(
            f"{icon} {v.scheme_name}: confidence={v.confidence_score:.2f} ({v.verdict})"
        )
    summary = "\n".join(summary_parts)
    
    return {
        "verification": {
            "overall_confidence": result.overall_confidence,
            "num_verified": result.num_verified,
            "num_needs_review": result.num_needs_review,
            "num_unverified": result.num_unverified,
            "details": [
                {
                    "scheme": v.scheme_name,
                    "confidence": v.confidence_score,
                    "verdict": v.verdict,
                    "citation_present": v.citation_present,
                    "similarity": v.retrieval_similarity,
                    "coverage": v.claim_coverage,
                    "source_url": v.source_url,
                }
                for v in result.claim_verifications
            ],
        },
        "verification_summary": summary,
        "overall_confidence": result.overall_confidence,
        "agent_trace": state.get("agent_trace", []) + [
            f"[Verification Agent] Overall confidence: {result.overall_confidence:.2f} "
            f"(Verified: {result.num_verified}, Review: {result.num_needs_review}, "
            f"Unverified: {result.num_unverified})"
        ],
    }


def opportunity_node(state: SetuState) -> dict:
    """Run Opportunity agent."""
    store = SetuVectorStore()
    agent = OpportunityAgent(vector_store=store)
    
    result = agent.run(
        query=state.get("query_en", state["user_message"]),
        user_profile=state.get("user_profile", {}),
    )
    
    return {
        "opportunity": {
            "response_text": result.response_text,
            "opportunities_found": result.opportunities_found,
            "status": result.status,
        },
        "agent_trace": state.get("agent_trace", []) + [
            f"[Opportunity Agent] Found {len(result.opportunities_found)} opportunities"
        ],
    }


def planner_node(state: SetuState) -> dict:
    """Run Planner & Action agent."""
    agent = PlannerAgent()
    
    elig_text = state.get("eligibility", {}).get("response_text", "")
    opp_text = state.get("opportunity", {}).get("response_text", "")
    verif_summary = state.get("verification_summary", "")
    language = state.get("detected_language", "en")
    
    result = agent.run(
        user_query=state.get("query_en", state["user_message"]),
        eligibility_response=elig_text,
        opportunity_response=opp_text,
        verification_summary=verif_summary,
        language=language,
    )
    
    return {
        "plan": {
            "action_plan": result.action_plan,
            "document_checklist": result.document_checklist,
            "num_steps": result.num_steps,
        },
        "agent_trace": state.get("agent_trace", []) + [
            f"[Planner Agent] Created action plan with {len(result.document_checklist)} documents needed"
        ],
    }


def compose_response_node(state: SetuState) -> dict:
    """Compose the final response from all agent outputs."""
    language = state.get("detected_language", "en")
    
    parts = []
    
    # Eligibility section
    elig = state.get("eligibility", {})
    if elig and elig.get("response_text"):
        parts.append(elig["response_text"])
    
    # Verification warnings
    verif = state.get("verification", {})
    if verif and verif.get("num_needs_review", 0) > 0:
        if language == "hi":
            parts.append("\n--- सत्यापन नोट ---")
        else:
            parts.append("\n--- Verification Notes ---")
        parts.append(state.get("verification_summary", ""))
    
    # Opportunities
    opp = state.get("opportunity", {})
    if opp and opp.get("response_text") and opp.get("status") != "no_results":
        if language == "hi":
            parts.append("\n--- अवसर ---")
        else:
            parts.append("\n--- Opportunities ---")
        parts.append(opp["response_text"])
    
    # Action plan
    plan = state.get("plan", {})
    if plan and plan.get("action_plan"):
        if language == "hi":
            parts.append("\n--- कार्य योजना ---")
        else:
            parts.append("\n--- Action Plan ---")
        parts.append(plan["action_plan"])
    
    final = "\n\n".join(parts) if parts else "I could not find relevant information for your query."
    
    return {
        "final_response": final,
        "agent_trace": state.get("agent_trace", []) + [
            "[Orchestrator] Response composed"
        ],
    }


# --- Routing Functions ---

def route_after_language(state: SetuState) -> str:
    """Determine which agents to run based on detected intent."""
    intent = state.get("intent", "find_schemes")
    
    if intent == "find_opportunities":
        return "opportunity"
    elif intent in ("find_schemes", "check_eligibility", "get_documents_list", "application_help"):
        return "eligibility"
    else:
        # General questions and combined queries go through eligibility
        return "eligibility"


def route_after_eligibility(state: SetuState) -> str:
    """After eligibility, always verify."""
    return "verification"


def route_after_verification(state: SetuState) -> str:
    """After verification, check if we should also find opportunities."""
    intent = state.get("intent", "")
    # For most queries, also check opportunities
    return "opportunity"


# --- Build the Graph ---

def build_orchestrator() -> StateGraph:
    """
    Build the LangGraph orchestrator with conditional routing.
    
    Graph structure:
        language -> [eligibility | opportunity]  (conditional)
        eligibility -> verification
        verification -> opportunity
        opportunity -> planner
        planner -> compose_response -> END
    """
    graph = StateGraph(SetuState)
    
    # Add nodes
    graph.add_node("language", language_node)
    graph.add_node("eligibility", eligibility_node)
    graph.add_node("verification", verification_node)
    graph.add_node("opportunity", opportunity_node)
    graph.add_node("planner", planner_node)
    graph.add_node("compose_response", compose_response_node)
    
    # Set entry point
    graph.set_entry_point("language")
    
    # Add conditional routing after language detection
    graph.add_conditional_edges(
        "language",
        route_after_language,
        {
            "eligibility": "eligibility",
            "opportunity": "opportunity",
        }
    )
    
    # Linear flow: eligibility -> verification -> opportunity -> planner -> compose
    graph.add_edge("eligibility", "verification")
    graph.add_edge("verification", "opportunity")
    graph.add_edge("opportunity", "planner")
    graph.add_edge("planner", "compose_response")
    graph.add_edge("compose_response", END)
    
    return graph


def run_setu(user_message: str) -> dict:
    """
    Run the full SETU pipeline on a user message.
    
    Returns the final state dict with all agent outputs.
    """
    graph = build_orchestrator()
    app = graph.compile()
    
    initial_state = {
        "user_message": user_message,
        "detected_language": "en",
        "intent": "",
        "user_profile": {},
        "query_en": "",
        "intake": None,
        "eligibility": None,
        "verification": None,
        "opportunity": None,
        "plan": None,
        "eligible_schemes": [],
        "verification_summary": "",
        "overall_confidence": 0.0,
        "final_response": "",
        "agent_trace": [],
    }
    
    result = app.invoke(initial_state)
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("SETU Orchestrator — Full Pipeline Test")
    print("=" * 60)
    
    query = "I am an SC student from Rajasthan, my family income is 2 lakh per year. I passed 12th with 65%. What scholarships and opportunities can I get?"
    
    print(f"\nUser: {query}\n")
    print("Running full pipeline (this may take 2-3 minutes)...")
    print("-" * 60)
    
    result = run_setu(query)
    
    print("\n" + "=" * 60)
    print("AGENT TRACE:")
    print("=" * 60)
    for step in result.get("agent_trace", []):
        print(f"  {step}")
    
    print("\n" + "=" * 60)
    print("FINAL RESPONSE:")
    print("=" * 60)
    print(result.get("final_response", "No response generated"))
    
    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("=" * 60)
    print(f"Overall Confidence: {result.get('overall_confidence', 0):.3f}")
    print(result.get("verification_summary", "N/A"))
