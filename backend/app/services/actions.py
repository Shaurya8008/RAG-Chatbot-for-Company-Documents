import httpx
import json
import logging
from typing import Dict, Any, List

from app.config import settings

logger = logging.getLogger(__name__)

class ActionService:
    """Service to handle workflow integrations and actions."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_llm_model

    async def classify_intent(self, query: str) -> str:
        """Classify if the query is a standard question or an action request."""
        prompt = f"""Classify the following user request into exactly ONE of these categories:
- DRAFT_EMAIL: The user is asking to draft, write, or compose an email to someone.
- CREATE_TICKET: The user is asking to log a bug, create a ticket, or file an issue.
- QUESTION: The user is asking a general question or asking for information (default).

User Request: "{query}"

Reply with ONLY the exact category name (DRAFT_EMAIL, CREATE_TICKET, or QUESTION). Do not include any other text."""
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {"temperature": 0.0}
                    }
                )
                response.raise_for_status()
                response_text = response.json().get("message", {}).get("content", "").strip().upper()
                
                # Robust parsing
                if "DRAFT_EMAIL" in response_text:
                    return "DRAFT_EMAIL"
                elif "CREATE_TICKET" in response_text:
                    return "CREATE_TICKET"
                
                return "QUESTION"
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return "QUESTION"

    def _build_action_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Combine retrieved chunks into a single context string."""
        if not chunks:
            return "No relevant company documents were found."
        
        texts = [c.get("content", "") for c in chunks]
        return "\n\n".join(texts)

    async def execute_action(self, intent: str, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the action and return structured results."""
        context_text = self._build_action_context(retrieved_chunks)
        
        if intent == "DRAFT_EMAIL":
            prompt = f"""You are an AI assistant. The user wants to draft a professional email based on company documents.
            
Company Policy Context:
{context_text}

User Request: "{query}"

Draft the email. Start directly with "Subject: " and then the body. Do not include any other conversational filler."""
        else: # CREATE_TICKET
            prompt = f"""You are an AI assistant. The user wants to create a ticket or bug report.
            
Context (if relevant):
{context_text}

User Request: "{query}"

Draft the ticket. Format it with:
Title: [Ticket Title]
Priority: [High/Medium/Low]
Description: [Ticket Description]

Do not include any conversational filler."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {"temperature": 0.2}
                    }
                )
                response.raise_for_status()
                result_text = response.json().get("message", {}).get("content", "").strip()
                
                # Here we could actually call Google API to create the draft, 
                # but for the pilot we just return the text to display in a UI widget.
                return {
                    "type": "action_result",
                    "action": intent,
                    "content": result_text,
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                "type": "action_result",
                "action": intent,
                "content": "Sorry, I encountered an error while trying to execute this action.",
                "status": "error"
            }

action_service = ActionService()
