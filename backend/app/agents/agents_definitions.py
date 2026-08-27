from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.api.v1 import schemas
from app.rag.retriever import retriever
from app.db import crud
from app.db.base import SessionLocal
from app.core.logging import logger
import json

# Placeholder for LLM initialization to avoid runtime errors if keys missing
# MockLLM for fallback
class MockLLM:
    def invoke(self, messages):
        # Determine intent from prompt content
        content = messages[0].content
        if "Classify the query" in content:
            return type("MockResponse", (), {"content": json.dumps({"route": "retrieval", "confidence": 0.9})})
        elif "Answer the user's question" in content:
            return type("MockResponse", (), {"content": json.dumps({"answer": "This is a mock response because the LLM API key is missing.", "sources": []})})
        return type("MockResponse", (), {"content": "Mock response"})

from app.core.config import settings
import os

if settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("gsk_"):
     logger.warn("Invalid GROQ_API_KEY format. Using MockLLM.")
     llm = MockLLM()
elif settings.GROQ_API_KEY:
    try:
        # Groq decommissioned every Llama chat model (2026-08); the free
        # production line-up is now the openai/gpt-oss-* family. gpt-oss is a
        # reasoning model, so hide the chain of thought - the agents below parse
        # `.content` as JSON and would otherwise choke on the reasoning text.
        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            api_key=settings.GROQ_API_KEY,
            reasoning_format="hidden",
            reasoning_effort="low",
        )
    except Exception as e:
        logger.error(f"Failed to init ChatGroq: {e}. Using MockLLM.")
        llm = MockLLM()
else:
    logger.warn("GROQ_API_KEY not found. Using MockLLM.")
    llm = MockLLM()

class QueryAgent:
    """
    Decides where to route the query.
    """
    def route(self, state: Dict):
        query = state["query"]
        logger.info(f"QueryAgent processing: {query}")
        
        # Zero-shot classifier prompt
        prompt = f"""
        You are an intelligent router for an ops assistant.
        Classify the query into one of: 
        - 'retrieval': for SOP/policy questions (e.g., "how to...", "what is the limit...").
        - 'ops_monitor': for incident reports, errors, system failures (e.g., "System failure in database", "Server down", "Error 500").
        - 'weekly_summary': for requests about weekly reports.
        
        Return JSON: {{ "route": "...", "confidence": float }}
        Query: {query}
        """
        response = llm.invoke([HumanMessage(content=prompt)]).content
        logger.info(f"QueryAgent LLM Raw Response: {response}")
        
        try:
            # Flexible JSON extraction
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                decision = json.loads(json_str)
            else:
                decision = json.loads(response) # Try direct parse
        except Exception as e:
            logger.error(f"QueryAgent JSON Parsing Error: {e}")
            decision = {"route": "ops_monitor", "confidence": 0.5} # Fail-safe to ops_monitor for testing if parsing fails? No, stick to retrieval but log it.
            # Actually, let's look at the fallback. 
            decision = {"route": "retrieval", "confidence": 1.0}
            
        return {"next": decision.get("route", "retrieval")}

class RetrievalAgent:
    """
    RAG Answer Generator.
    """
    async def retrieve_and_answer(self, state: Dict):
        query = state["query"]
        docs = await retriever.retrieve(query)
        
        # Context construction
        context_str = "\n".join([f"Source: {d['filename']}\nContent: {d['text']}" for d in docs])
        
        prompt = f"""
        You are an operations assistant. Answer the user's question based strictly on the provided context.
        If the answer is not in the context, say "I don't have information about that in my documents." (unless it's a greeting).
        
        Context:
        {context_str}
        
        Question: {query}
        
        Return ONLY a JSON object with this format: {{ "answer": "...", "sources": [...] }}
        """
        
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            # Simple JSON extraction
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                data = json.loads(content[start:end])
                answer = data.get("answer", "Error parsing answer.")
            else:
                answer = content
        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            answer = "Sorry, I encountered an issue generating the response."
        
        return {
            "answer": answer,
            "sources": docs,
            "final_response": True
        }

class OpsMonitorAgent:
    """
    Analyzes logs/incidents.
    """
    async def analyze(self, state: Dict):
        log_entry = state.get("log_entry")
        query = state.get("query")
        
        # If coming from chat (no log_entry), treat query as the log message
        if not log_entry and query:
            log_entry = {
                "type": "ERROR" if "failure" in query.lower() or "critical" in query.lower() else "WARN",
                "message": query,
                "meta": {"source": "chat"}
            }
            # Update state for downstream agents
            # Note: In LangGraph, we return what we want to UPDATE in state. 
            # We assume state is merged. But here we return "next" mostly.
            # To pass log_entry to TicketAgent, we need to ensure it's in state. 
            # We might need to return it here if LangGraph supports it, 
            # but let's rely on TicketAgent using 'query' as description if log_entry missing.
        
        if not log_entry:
            return {"next": "end"}
            
        # Rule based check
        is_incident = False
        message = log_entry.get("message", "").lower()
        if "ERROR" in log_entry.get("type", "") or "failure" in message or "down" in message:
            is_incident = True
            
        if is_incident:
            # Pass severity and log_entry (if we constructed it) to state
            return {
                "next": "ticket_creation", 
                "severity": "high",
                "log_entry": log_entry # Update state with constructed log entry
            }
        return {"next": "end"}

class TicketAgent:
    """
    Creates tickets.
    """
    def create_ticket(self, state: Dict):
        db = SessionLocal()
        try:
            ticket = crud.create_ticket(db, schemas.TicketCreate(
                title=f"Incident: {state.get('query', 'Log Alert')}",
                description=state.get("log_entry", {}).get("message", "No desc"),
                severity=state.get("severity", "medium")
            ))
            logger.info(f"Ticket created: {ticket.id}")
            return {"ticket_id": str(ticket.id), "next": "notification"}
        finally:
            db.close()

class NotificationAgent:
    """
    Sends alerts.
    """
    def send_alert(self, state: Dict):
        logger.info(f"NotificationAgent: Sending alert for Ticket {state.get('ticket_id')}")
        # In a real app, we would send Email/Slack here.
        # For now, we just log it as 'sent'
        return {"notification_sent": True, "final_response": True}

class WeeklySummaryAgent:
    def generate(self, state: Dict):
        logger.info("Generating weekly summary...")
        db = SessionLocal()
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            logs = crud.get_logs_by_range(db, start_date, end_date)
            # We don't have a direct 'get_tickets_by_range' in crud but we can assume 'get_dashboard_stats' gives us some info
            # Or just hack it for now since we want to be robust
            
            summary_text = f"Weekly Summary ({start_date.date()} to {end_date.date()}):\n"
            summary_text += f"- Logs Analyzed: {len(logs)}\n"
            
            # Simple aggregation
            errors = [l for l in logs if "ERROR" in l.type]
            if errors:
                summary_text += f"- Critical Issues: {len(errors)} errors found.\n"
            else:
                summary_text += "- System Health: Nominal. No errors found.\n"
                
            return {
                "answer": summary_text,
                "summary_stats": {
                    "start_date": str(start_date.date()),
                    "end_date": str(end_date.date()),
                    "total_logs_analyzed": len(logs),
                    "tickets_created": 0, # Placeholder, would query tickets
                    "top_issues": [l.type for l in errors[:5]] if errors else [],
                },
                "final_response": True
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"answer": "Failed to generate summary.", "final_response": True}
        finally:
            db.close()
