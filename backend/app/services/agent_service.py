import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.email import Email
from app.models.action import Action
from app.schemas.agent import AgentStep, AgentTrace
from app.services.agent_tools import AgentTools

class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_steps = 6
    
    async def run_agent(
        self,
        email_id: str,
        classification: Dict[str, Any],
        is_dry_run: bool = False
    ) -> AgentTrace:
        tools = AgentTools(self.db, is_dry_run=is_dry_run)
        steps: List[AgentStep] = []
        
        # Get email details
        stmt = select(Email).where(Email.id == email_id)
        result = await self.db.execute(stmt)
        email = result.scalar_one_or_none()
        
        if email is None:
            return AgentTrace(
                email_id=email_id,
                classification=classification,
                steps=[],
                final_recommendation="Email not found",
                escalate=True,
                escalation_brief="Email record not found in database",
                tools_used=[],
                completed_at=datetime.utcnow(),
                dry_run=is_dry_run
            )
        
        # Build email context
        email_context = {
            "sender": email.sender,
            "subject": email.subject,
            "body_preview": email.body[:500],
            "urgency": classification.get("urgency", "Low"),
            "category": classification.get("category", "General"),
            "requires_human": classification.get("requires_human", False)
        }
        
        # Build tool list description
        tool_descriptions = """
- search_knowledge_base(query: str): Search internal policy documents
- get_thread_history(sender_email: str): Get email thread history
- get_contact_profile(email: str): Get contact VIP/tier info
- check_account_status(email: str): Get billing/subscription status
- draft_reply(context: str, tone: str, policy_refs: list): Draft a reply
- escalate_to_human(email_id: str, reason: str, priority: str): Escalate to human
- create_internal_ticket(title: str, body: str, assignee: str): Create ticket
- scrape_public_sentiment(company_name: str): Check public reviews
- flag_for_legal(email_id: str, issue_type: str): Flag for legal review
- send_auto_reply(email_id: str, draft_id: str): Send an auto-reply
"""
        
        # Initial thought
        current_thought = f"I need to handle this email from {email.sender}. Category: {classification.get('category')}. Urgency: {classification.get('urgency')}."
        
        # Check critical conditions
        if classification.get("urgency") == "Critical" or classification.get("requires_human"):
            current_thought += " This requires immediate human attention due to critical urgency or policy requirements."
        
        # Step 1: Always get thread history if available
        step1 = AgentStep(
            step_number=1,
            thought=f"First, I need to understand the full context by getting thread history for {email.sender}.",
            action="get_thread_history",
            action_input={"sender_email": email.sender}
        )
        step1_obs = await tools.execute("get_thread_history", {"sender_email": email.sender})
        step1.observation = json.dumps(step1_obs.get("result", {}), default=str)[:1000]
        steps.append(step1)
        
        thread_count = len(step1_obs.get("result", []))
        
        # Step 2: Get contact profile
        step2 = AgentStep(
            step_number=2,
            thought="Next, I'll check the contact profile to understand account value and VIP status.",
            action="get_contact_profile",
            action_input={"email": email.sender}
        )
        step2_obs = await tools.execute("get_contact_profile", {"email": email.sender})
        step2.observation = json.dumps(step2_obs.get("result", {}), default=str)[:1000]
        steps.append(step2)
        
        contact_profile = step2_obs.get("result", {})
        is_vip = contact_profile.get("vip_status", False)
        account_value = contact_profile.get("account_value", 0)
        
        # Determine if escalation is needed
        escalate = False
        escalation_reason = ""
        draft_reply = None
        
        if classification.get("urgency") == "Critical":
            escalate = True
            escalation_reason = f"Critical urgency detected. Category: {classification.get('category')}."
        elif classification.get("requires_human"):
            escalate = True
            escalation_reason = f"Classification requires human review. Confidence: {classification.get('confidence', 0)}"
        elif is_vip and account_value > 1000 and classification.get("sentiment_score", 0) < -0.4:
            escalate = True
            escalation_reason = f"VIP account ({account_value}/mo) with negative sentiment."
        
        if escalate:
            # Search knowledge base for relevant policies
            step3 = AgentStep(
                step_number=3,
                thought=f"This needs escalation. Let me search the knowledge base for relevant policies to include in the escalation brief.",
                action="search_knowledge_base",
                action_input={"query": f"{classification.get('category')} {email.subject or ''}"}
            )
            step3_obs = await tools.execute("search_knowledge_base", {"query": f"{classification.get('category')} {email.subject or ''}"})
            step3.observation = json.dumps(step3_obs.get("result", []), default=str)[:1000]
            steps.append(step3)
            
            # Escalate
            step4 = AgentStep(
                step_number=4,
                thought="I have enough information. I will escalate this to the human review queue.",
                action="escalate_to_human",
                action_input={
                    "email_id": str(email.id),
                    "reason": escalation_reason,
                    "priority": classification.get("urgency", "Medium")
                }
            )
            step4_obs = await tools.execute("escalate_to_human", {
                "email_id": str(email.id),
                "reason": escalation_reason,
                "priority": classification.get("urgency", "Medium")
            })
            step4.observation = json.dumps(step4_obs.get("result", {}), default=str)[:1000]
            steps.append(step4)
            
            # Flag for legal if needed
            if classification.get("category") == "Compliance":
                step5 = AgentStep(
                    step_number=5,
                    thought="This is a compliance matter. I must also flag for legal review.",
                    action="flag_for_legal",
                    action_input={"email_id": str(email.id), "issue_type": classification.get("subcategory", "Compliance")}
                )
                step5_obs = await tools.execute("flag_for_legal", {"email_id": str(email.id), "issue_type": classification.get("subcategory", "Compliance")})
                step5.observation = json.dumps(step5_obs.get("result", {}), default=str)[:1000]
                steps.append(step5)
            
            final_recommendation = "Escalate to human team"
        else:
            # Not escalating - try to draft reply
            step3 = AgentStep(
                step_number=3,
                thought="This does not require escalation. I will search the knowledge base to draft an accurate reply.",
                action="search_knowledge_base",
                action_input={"query": f"{classification.get('category')} {email.subject or ''}"}
            )
            step3_obs = await tools.execute("search_knowledge_base", {"query": f"{classification.get('category')} {email.subject or ''}"})
            step3.observation = json.dumps(step3_obs.get("result", []), default=str)[:1000]
            steps.append(step3)
            
            policy_refs = []
            for chunk in step3_obs.get("result", []):
                policy_refs.append(f"{chunk.get('source')}:{chunk.get('heading', '')}")
            
            step4 = AgentStep(
                step_number=4,
                thought="Now I'll draft a reply based on the policy context and thread history.",
                action="draft_reply",
                action_input={
                    "context": f"Email from {email.sender} about {email.subject}. Category: {classification.get('category')}",
                    "tone": "professional",
                    "policy_refs": policy_refs
                }
            )
            step4_obs = await tools.execute("draft_reply", {
                "context": f"Email from {email.sender} about {email.subject}. Category: {classification.get('category')}",
                "tone": "professional",
                "policy_refs": policy_refs
            })
            step4.observation = json.dumps(step4_obs.get("result", {}), default=str)[:1000]
            steps.append(step4)
            
            draft_reply = step4_obs.get("result", {}).get("draft", "")
            final_recommendation = "Draft reply and queue for review"
            
            # Optionally send if confidence is high enough
            if classification.get("confidence", 0) > 0.85 and classification.get("urgency") != "Critical":
                step5 = AgentStep(
                    step_number=5,
                    thought="Confidence is high. I will proceed to send the auto-reply.",
                    action="send_auto_reply",
                    action_input={"email_id": str(email.id), "draft_id": "draft-" + str(email.id)[:8]}
                )
                step5_obs = await tools.execute("send_auto_reply", {"email_id": str(email.id), "draft_id": "draft-" + str(email.id)[:8]})
                step5.observation = json.dumps(step5_obs.get("result", {}), default=str)[:1000]
                steps.append(step5)
                final_recommendation = "Auto-reply sent"
        
        tools_used = list(set(s.action for s in steps if s.action != "FINISH"))
        
        trace = AgentTrace(
            email_id=email_id,
            classification=classification,
            steps=steps,
            final_recommendation=final_recommendation,
            draft_reply=draft_reply,
            escalate=escalate,
            escalation_brief=escalation_reason if escalate else None,
            tools_used=tools_used,
            completed_at=datetime.utcnow(),
            dry_run=is_dry_run
        )
        
        # Store reasoning trace in DB if not dry run
        if not is_dry_run:
            await self._store_trace(email_id, trace)
        
        return trace
    
    async def _store_trace(self, email_id: str, trace: AgentTrace):
        try:
            import json
            from datetime import datetime
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
            
            action = Action(
                email_id=email_id,
                action_type="Agent-Run",
                status="Completed",
                description=trace.final_recommendation,
                agent_reasoning_log=json.loads(json.dumps([step.model_dump() for step in trace.steps], default=serialize_datetime))
            )
            self.db.add(action)
            await self.db.flush()
        except Exception:
            pass
    
    async def dry_run(self, email_id: str, classification: Dict[str, Any]) -> AgentTrace:
        return await self.run_agent(email_id, classification, is_dry_run=True)
