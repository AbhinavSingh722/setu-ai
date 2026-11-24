"""
SETU Planner & Action Agent

Final agent in the pipeline — takes scheme/opportunity recommendations and
produces an actionable checklist with specific steps, documents to gather,
and draft messages the user can send for inquiries.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

PLANNER_SYSTEM_PROMPT = """You are the Planner & Action Agent for SETU. Your job is to create a clear, actionable plan for the user based on the scheme/opportunity recommendations they've received.

OUTPUT FORMAT — Produce a structured action plan:

1. DOCUMENT CHECKLIST: List every document the user needs to gather, with where to get it
2. STEP-BY-STEP PLAN: Numbered steps to apply, in order of priority  
3. IMPORTANT DEADLINES: Any known deadlines or timing considerations
4. DRAFT MESSAGE (if applicable): A message the user can send to their local office for help

RULES:
- Keep language simple — the user may have low literacy
- If responding in Hindi, use simple Hindi (not formal/literary)
- Be specific: "Go to Gram Panchayat office" not "Visit relevant authority"
- Include portal URLs where applicable
- Prioritize by impact (highest benefit first)
- Always mention free helpline numbers if available
"""


@dataclass
class PlannerResult:
    """Result from the Planner agent."""
    action_plan: str
    document_checklist: list
    num_steps: int
    agent_name: str = "Planner & Action Agent"
    status: str = "completed"


class PlannerAgent:
    """Creates actionable plans from scheme/opportunity recommendations."""
    
    def __init__(
        self,
        model_name: str = None,
    ):
        self.llm = ChatGroq(
            model=model_name or GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=1024,
        )
    
    def run(
        self,
        user_query: str,
        eligibility_response: str = "",
        opportunity_response: str = "",
        verification_summary: str = "",
        language: str = "en",
    ) -> PlannerResult:
        """
        Generate an action plan from agent responses.
        
        Args:
            user_query: Original user query
            eligibility_response: Eligibility agent's response text
            opportunity_response: Opportunity agent's response text
            verification_summary: Verification summary string
            language: "en" or "hi"
        """
        lang_instruction = (
            "Respond in simple Hindi (हिंदी में जवाब दें)." 
            if language == "hi" else 
            "Respond in simple English."
        )
        
        prompt = f"""Based on the following information, create a clear action plan for the user.

USER'S SITUATION: {user_query}

ELIGIBLE SCHEMES:
{eligibility_response}

OPPORTUNITIES:
{opportunity_response if opportunity_response else "No additional opportunities found."}

VERIFICATION NOTES:
{verification_summary if verification_summary else "All recommendations are from verified source documents."}

{lang_instruction}

Create the action plan now. Include a document checklist, step-by-step plan, and a draft message for the local office."""
        
        try:
            messages = [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            action_plan = response.content
        except Exception as e:
            action_plan = f"Error generating plan: {str(e)}"
        
        # Extract document mentions
        doc_keywords = [
            "Aadhaar", "aadhaar", "caste certificate", "income certificate",
            "domicile", "mark sheet", "bank account", "BPL", "ration card",
            "Jan Aadhaar", "passport", "photograph", "birth certificate",
            "death certificate", "disability certificate",
        ]
        docs_found = [kw for kw in doc_keywords if kw.lower() in action_plan.lower()]
        
        return PlannerResult(
            action_plan=action_plan,
            document_checklist=list(set(docs_found)),
            num_steps=action_plan.count("\n") // 2,  # Rough step count
        )


if __name__ == "__main__":
    agent = PlannerAgent()
    result = agent.run(
        user_query="SC student, Rajasthan, 12th pass, income 2 lakh",
        eligibility_response="Post-Matric SC Scholarship, Rajasthan Uttar Matric Scholarship",
        language="en",
    )
    print(f"Plan:\n{result.action_plan}")
    print(f"\nDocs needed: {result.document_checklist}")
