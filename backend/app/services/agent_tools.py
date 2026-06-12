import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.email import Email
from app.models.action import Action
from app.models.contact import Contact
from app.models.thread import Thread
from app.schemas.agent import AgentStep, AgentTrace
from app.services.rag_service import rag_service
from app.config import settings

class AgentTools:
    def __init__(self, db: AsyncSession, is_dry_run: bool = False):
        self.db = db
        self.is_dry_run = is_dry_run
    
    async def search_knowledge_base(self, query: str) -> Dict[str, Any]:
        chunks = await rag_service.search(self.db, query, top_k=3)
        return {
            "tool": "search_knowledge_base",
            "result": [
                {
                    "source": c.source,
                    "heading": c.heading,
                    "content": c.content[:500],
                    "score": c.score
                }
                for c in chunks
            ]
        }
    
    async def get_thread_history(self, sender_email: str) -> Dict[str, Any]:
        stmt = select(Thread).where(Thread.sender_email == sender_email).order_by(Thread.created_at.desc())
        result = await self.db.execute(stmt)
        threads = result.scalars().all()
        
        history = []
        for thread in threads[:5]:
            emails = []
            for email in thread.emails[:10]:
                emails.append({
                    "id": str(email.id),
                    "subject": email.subject,
                    "timestamp": email.timestamp.isoformat(),
                    "category": email.category,
                    "sentiment_score": email.sentiment_score,
                    "status": email.status
                })
            history.append({
                "thread_id": str(thread.id),
                "category": thread.category,
                "status": thread.status,
                "emails": emails
            })
        
        return {"tool": "get_thread_history", "result": history}
    
    async def get_contact_profile(self, email: str) -> Dict[str, Any]:
        stmt = select(Contact).where(Contact.email == email)
        result = await self.db.execute(stmt)
        contact = result.scalar_one_or_none()
        
        if contact:
            thread_stmt = select(Thread).where(
                Thread.sender_email == email,
                Thread.status != "Closed"
            )
            thread_result = await self.db.execute(thread_stmt)
            open_threads = len(thread_result.scalars().all())
            
            return {
                "tool": "get_contact_profile",
                "result": {
                    "email": contact.email,
                    "name": contact.name,
                    "tier": contact.tier,
                    "account_value": contact.account_value,
                    "vip_status": contact.vip_status,
                    "churn_risk_score": contact.churn_risk_score,
                    "open_threads": open_threads
                }
            }
        
        return {"tool": "get_contact_profile", "result": None}
    
    async def check_account_status(self, email: str) -> Dict[str, Any]:
        profile = await self.get_contact_profile(email)
        if profile["result"]:
            return {
                "tool": "check_account_status",
                "result": {
                    "tier": profile["result"]["tier"],
                    "account_value": profile["result"]["account_value"],
                    "status": "Active",
                    "overdue_invoices": 0,
                    "notes": "Simulated billing status"
                }
            }
        return {"tool": "check_account_status", "result": {"status": "Unknown"}}
    
    async def draft_reply(self, context: str, tone: str, policy_refs: List[str]) -> Dict[str, Any]:
        draft = await self._generate_llm_reply(context, tone, policy_refs)
        
        return {"tool": "draft_reply", "result": {"draft": draft, "tone": tone}}
    
    async def _generate_llm_reply(self, context: str, tone: str, policy_refs: List[str]) -> str:
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_key_here":
            return self._template_reply(context, tone, policy_refs)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "SenAI CRM"
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are a customer support agent drafting a reply email.
Tone: {tone}.
Reference these policies: {', '.join(policy_refs)}.
Write a professional, empathetic, and specific reply. Cite specific policy details where relevant.
Do NOT admit legal liability. Do NOT make promises you can't keep.
Return ONLY the email body text, no preamble."""
                            },
                            {
                                "role": "user",
                                "content": f"Draft a reply for this context:\n{context[:2000]}"
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 512
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return self._template_reply(context, tone, policy_refs)
    
    def _template_reply(self, context: str, tone: str, policy_refs: List[str]) -> str:
        draft = f"Dear Customer,\n\nThank you for reaching out to us. "
        draft += f"We have reviewed your inquiry regarding the details you provided.\n\n"
        if policy_refs:
            draft += f"Based on our policies ({', '.join(policy_refs[:3])}), "
            draft += f"we would like to inform you of the following:\n\n"
        draft += "Our team is actively looking into this matter and we will provide a detailed response within 24 hours.\n\n"
        draft += "If you have any immediate concerns, please don't hesitate to reply to this email.\n\n"
        draft += "Best regards,\nSenAI Support Team"
        return draft
    
    async def escalate_to_human(self, email_id: str, reason: str, priority: str) -> Dict[str, Any]:
        if not self.is_dry_run:
            action = Action(
                email_id=email_id,
                action_type="Escalation",
                status="Pending",
                description=f"Escalated: {reason}",
                assigned_to="human_review_queue"
            )
            self.db.add(action)
            await self.db.flush()
        
        return {
            "tool": "escalate_to_human",
            "result": {
                "escalation_id": "esc-" + email_id[:8],
                "reason": reason,
                "priority": priority,
                "status": "escalated"
            }
        }
    
    async def create_internal_ticket(self, title: str, body: str, assignee: str) -> Dict[str, Any]:
        if not self.is_dry_run:
            action = Action(
                email_id="00000000-0000-0000-0000-000000000000",
                action_type="Ticket-Created",
                status="Open",
                description=f"{title}\n{body}",
                assigned_to=assignee
            )
            self.db.add(action)
            await self.db.flush()
        
        return {
            "tool": "create_internal_ticket",
            "result": {
                "ticket_id": "ticket-" + str(hash(title))[:8],
                "title": title,
                "assignee": assignee,
                "status": "open"
            }
        }
    
    async def scrape_public_sentiment(self, company_name: str) -> Dict[str, Any]:
        return {
            "tool": "scrape_public_sentiment",
            "result": {
                "company": company_name,
                "g2_rating": 4.2,
                "g2_review_count": 150,
                "common_themes": ["Good UI", "Slow support", "Feature requests"],
                "source": "cached_or_simulated"
            }
        }
    
    async def flag_for_legal(self, email_id: str, issue_type: str) -> Dict[str, Any]:
        if not self.is_dry_run:
            action = Action(
                email_id=email_id,
                action_type="Legal-Flag",
                status="Open",
                description=f"Legal flag: {issue_type}",
                assigned_to="legal@company.com"
            )
            self.db.add(action)
            await self.db.flush()
        
        return {
            "tool": "flag_for_legal",
            "result": {
                "flag_id": "legal-" + email_id[:8],
                "issue_type": issue_type,
                "status": "flagged"
            }
        }
    
    async def send_auto_reply(self, email_id: str, draft_id: str) -> Dict[str, Any]:
        if not self.is_dry_run:
            stmt = select(Email).where(Email.id == email_id)
            result = await self.db.execute(stmt)
            email = result.scalar_one_or_none()
            if email:
                email.status = "Replied"
                await self.db.flush()
        
        return {
            "tool": "send_auto_reply",
            "result": {
                "email_id": email_id,
                "draft_id": draft_id,
                "status": "sent",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        method = getattr(self, tool_name, None)
        if method is None:
            return {"tool": tool_name, "error": f"Unknown tool: {tool_name}"}
        
        try:
            return await method(**params)
        except Exception as e:
            return {"tool": tool_name, "error": str(e)}
