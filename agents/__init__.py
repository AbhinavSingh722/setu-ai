"""
SETU Agents Package

Multi-agent system for matching citizens with government schemes.

Agents:
    - LanguageAgent: Language detection + intent extraction
    - EligibilityAgent: RAG-grounded scheme matching
    - VerificationAgent: Deterministic grounding score computation
    - OpportunityAgent: Skill/job opportunity matching
    - PlannerAgent: Action plan generation
    
Orchestrator:
    - run_setu(): Full pipeline via LangGraph
"""

from agents.language import LanguageAgent
from agents.eligibility import EligibilityAgent
from agents.verification import VerificationAgent
from agents.opportunity import OpportunityAgent
from agents.planner import PlannerAgent
from agents.orchestrator import run_setu, build_orchestrator

__all__ = [
    "LanguageAgent",
    "EligibilityAgent",
    "VerificationAgent",
    "OpportunityAgent",
    "PlannerAgent",
    "run_setu",
    "build_orchestrator",
]
