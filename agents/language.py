"""
SETU Language & Intake Agent

First agent in the pipeline — handles language detection, translates if needed,
and extracts structured user intent from natural language queries.

Supports Hindi and English. Uses Granite via Ollama for intent extraction.
"""

import os
import re
import json
from dataclasses import dataclass, field
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


INTAKE_SYSTEM_PROMPT = """You are the Language & Intake Agent for SETU. Your job is to:

1. Detect the language of the user's message (Hindi or English)
2. Extract structured information about the user's situation
3. Determine the user's intent (what kind of help they need)

You must output ONLY valid JSON with these fields:
{
    "detected_language": "hi" or "en",
    "intent": one of ["find_schemes", "check_eligibility", "find_opportunities", "get_documents_list", "application_help", "general_question"],
    "user_profile": {
        "category": "SC/ST/OBC/MBC/EWS/Minority/General or null",
        "state": "state name or null",
        "income": "annual income description or null",
        "age": "age or age range or null",
        "gender": "male/female or null",
        "education": "education level or null",
        "occupation": "occupation or null",
        "specific_need": "what they're looking for or null"
    },
    "query_summary_en": "brief English summary of the query for downstream agents",
    "original_query": "the original query as-is"
}

RULES:
- Always output ONLY the JSON, no extra text
- If information is not mentioned, set to null
- Be generous in extracting — infer category from context if possible
- "query_summary_en" must always be in English even if original is Hindi
- Handle mixed Hindi/English (Hinglish) naturally
"""


@dataclass
class IntakeResult:
    """Structured output from the Language & Intake agent."""
    detected_language: str  # "hi" or "en"
    intent: str  # find_schemes, check_eligibility, etc.
    user_profile: dict  # Extracted user details
    query_summary_en: str  # English summary for downstream agents
    original_query: str
    agent_name: str = "Language & Intake Agent"
    status: str = "completed"


class LanguageAgent:
    """
    Language & Intake Agent.
    
    First in the pipeline — processes raw user input into structured intent.
    """
    
    def __init__(
        self,
        model_name: str = None,
    ):
        self.llm = ChatGroq(
            model=model_name or GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.0,
            max_tokens=512,
        )
    
    def _detect_language_heuristic(self, text: str) -> str:
        """Quick heuristic language detection (backup for LLM)."""
        # Check for Devanagari script characters
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
        latin_count = len(re.findall(r'[a-zA-Z]', text))
        
        if devanagari_count > latin_count:
            return "hi"
        return "en"
    
    def _parse_llm_response(self, response_text: str, original_query: str) -> IntakeResult:
        """Parse LLM JSON response, with fallback for malformed output."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            return IntakeResult(
                detected_language=data.get("detected_language", self._detect_language_heuristic(original_query)),
                intent=data.get("intent", "find_schemes"),
                user_profile=data.get("user_profile", {}),
                query_summary_en=data.get("query_summary_en", original_query),
                original_query=original_query,
            )
        except (json.JSONDecodeError, ValueError):
            # Fallback: basic extraction without LLM
            return IntakeResult(
                detected_language=self._detect_language_heuristic(original_query),
                intent="find_schemes",
                user_profile={},
                query_summary_en=original_query,
                original_query=original_query,
                status="fallback",
            )
    
    def run(self, user_message: str) -> IntakeResult:
        """
        Process a user message into structured intent.
        
        Args:
            user_message: Raw user input (Hindi, English, or Hinglish)
            
        Returns:
            IntakeResult with language, intent, and extracted profile
        """
        messages = [
            SystemMessage(content=INTAKE_SYSTEM_PROMPT),
            HumanMessage(content=f"User message:\n{user_message}"),
        ]
        
        try:
            response = self.llm.invoke(messages)
            return self._parse_llm_response(response.content, user_message)
        except Exception as e:
            # If LLM fails, use heuristic fallback
            return IntakeResult(
                detected_language=self._detect_language_heuristic(user_message),
                intent="find_schemes",
                user_profile={},
                query_summary_en=user_message,
                original_query=user_message,
                status="error",
            )


if __name__ == "__main__":
    agent = LanguageAgent()
    
    # Test with English
    r1 = agent.run("I am an SC student from Rajasthan, family income 2 lakh. What scholarships?")
    print(f"EN: lang={r1.detected_language}, intent={r1.intent}")
    print(f"  Profile: {r1.user_profile}")
    print(f"  Summary: {r1.query_summary_en}")
    
    # Test with Hindi
    r2 = agent.run("मैं राजस्थान से SC छात्र हूँ, परिवार की आय 2 लाख है। कौन सी छात्रवृत्ति मिल सकती है?")
    print(f"\nHI: lang={r2.detected_language}, intent={r2.intent}")
    print(f"  Profile: {r2.user_profile}")
    print(f"  Summary: {r2.query_summary_en}")
