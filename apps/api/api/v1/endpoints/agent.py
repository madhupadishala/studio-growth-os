"""
Studio Growth OS - AI Sales Agent Endpoints
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from prisma import Prisma

from core.database import get_db
from core.logging import get_logger
from api.v1.endpoints.auth import get_tenant_context

logger = get_logger(__name__)

router = APIRouter()

# Tool definitions (matching the agent tool registry)
AGENT_TOOLS = {
    "check_availability": {
        "description": "Check available slots for a given occasion, date range, and duration",
        "parameters": {
            "type": "object",
            "properties": {
                "occasion": {"type": "string"},
                "date_range": {"type": "array", "items": {"type": "string", "format": "date"}},
                "duration_hours": {"type": "integer"},
            },
            "required": ["occasion", "date_range"],
        },
    },
    "calculate_quote": {
        "description": "Calculate a quote for a lead with package, add-ons, date, and location",
        "parameters": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "string"},
                "package_id": {"type": "string"},
                "addon_ids": {"type": "array", "items": {"type": "string"}},
                "event_date": {"type": "string", "format": "date"},
                "location": {"type": "string"},
                "discount_code": {"type": "string"},
            },
            "required": ["lead_id", "package_id", "event_date", "location"],
        },
    },
    "compare_packages": {
        "description": "Compare multiple packages side by side",
        "parameters": {
            "type": "object",
            "properties": {
                "package_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["package_ids"],
        },
    },
    "hold_slot": {
        "description": "Place a temporary hold on a resource for a time window",
        "parameters": {
            "type": "object",
            "properties": {
                "resource_ids": {"type": "array", "items": {"type": "string"}},
                "start_at": {"type": "string", "format": "date-time"},
                "end_at": {"type": "string", "format": "date-time"},
                "ttl_minutes": {"type": "integer", "default": 30},
            },
            "required": ["resource_ids", "start_at", "end_at"],
        },
    },
    "release_slot": {
        "description": "Release a temporary slot hold",
        "parameters": {
            "type": "object",
            "properties": {
                "hold_id": {"type": "string"},
            },
            "required": ["hold_id"],
        },
    },
    "send_quote": {
        "description": "Send a quote to the customer via specified channel",
        "parameters": {
            "type": "object",
            "properties": {
                "quote_id": {"type": "string"},
                "channel": {"type": "string", "enum": ["whatsapp", "email", "instagram_dm"]},
                "template_vars": {"type": "object"},
            },
            "required": ["quote_id"],
        },
    },
    "create_payment_link": {
        "description": "Create a Razorpay payment link for a quote",
        "parameters": {
            "type": "object",
            "properties": {
                "quote_id": {"type": "string"},
                "amount_paise": {"type": "integer"},
                "description": {"type": "string"},
            },
            "required": ["quote_id", "amount_paise"],
        },
    },
    "request_owner_approval": {
        "description": "Request owner approval for an action (discount, custom package, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "context": {"type": "object"},
            },
            "required": ["action", "context"],
        },
    },
    "handoff_to_human": {
        "description": "Escalate conversation to a human agent",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": ["reason", "urgency"],
        },
    },
}

# Schemas
class AgentConverseRequest(BaseModel):
    conversation_id: str
    message: str
    context: Optional[Dict[str, Any]] = {}

class ToolCall(BaseModel):
    tool: str
    arguments: Dict[str, Any]
    idempotency_key: str

class ToolResult(BaseModel):
    tool: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AgentConverseResponse(BaseModel):
    response: str
    tool_calls: List[ToolCall] = []
    tool_results: List[ToolResult] = []
    trace_id: str
    requires_approval: bool = False
    escalation_needed: bool = False

class AgentTraceResponse(BaseModel):
    id: str
    conversation_id: str
    tool_name: str
    input_json: Dict[str, Any]
    output_json: Optional[Dict[str, Any]]
    policy_decision: str
    latency_ms: int
    created_at: datetime

class KillSwitchRequest(BaseModel):
    enabled: bool
    reason: Optional[str] = None

# Endpoints
@router.get("/tools")
async def list_tools(
    tenant_ctx: dict = Depends(get_tenant_context),
):
    """List available agent tools with schemas"""
    return {
        "tools": [
            {
                "name": name,
                "description": spec["description"],
                "parameters": spec["parameters"],
            }
            for name, spec in AGENT_TOOLS.items()
        ]
    }

@router.post("/converse", response_model=AgentConverseResponse)
async def converse(
    request: AgentConverseRequest,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """
    Main agent conversation endpoint.
    Processes user message, executes tools, returns response.
    """
    # Verify conversation exists and belongs to tenant
    conversation = await db.conversation.find_first(
        where={"id": request.conversation_id, "tenantId": tenant_ctx["tenant_id"]}
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get lead context
    lead = await db.lead.find_unique(where={"id": conversation.leadId})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Build context for agent
    context = {
        "tenant_id": tenant_ctx["tenant_id"],
        "lead_id": conversation.leadId,
        "conversation_id": conversation.id,
        "lead_stage": lead.stage,
        "lead_score": lead.score,
        "event_date": lead.eventDate.isoformat() if lead.eventDate else None,
        "budget_band": lead.budgetBand,
        "policy_version": 1,  # from settings
        "approval_required": False,  # determined by policy engine
        "idempotency_key": f"conv_{conversation.id}_{datetime.utcnow().timestamp()}",
    }

    # Merge with request context
    context.update(request.context)

    # In production: Call LangGraph agent service
    # For now, return a structured response indicating tool calls needed

    # Simple keyword-based tool detection (placeholder for actual LLM)
    tool_calls = []
    response_text = "I'll help you with that. Let me check availability and calculate a quote."

    # Detect intent and suggest tool calls
    msg_lower = request.message.lower()

    if any(kw in msg_lower for kw in ["available", "availability", "free", "open", "slot"]):
        tool_calls.append(ToolCall(
            tool="check_availability",
            arguments={
                "occasion": "wedding",  # would be extracted by LLM
                "date_range": ["2026-12-15"],
                "duration_hours": 8,
            },
            idempotency_key=f"{context['idempotency_key']}_check_avail",
        ))

    if any(kw in msg_lower for kw in ["price", "cost", "quote", "package", "budget"]):
        tool_calls.append(ToolCall(
            tool="calculate_quote",
            arguments={
                "lead_id": conversation.leadId,
                "package_id": "pkg_full_marriage",  # would be determined by LLM
                "addon_ids": [],
                "event_date": "2026-12-15",
                "location": "Farmhouse X Shamirpet",
            },
            idempotency_key=f"{context['idempotency_key']}_calc_quote",
        ))

    if any(kw in msg_lower for kw in ["book", "confirm", "hold", "reserve"]):
        tool_calls.append(ToolCall(
            tool="hold_slot",
            arguments={
                "resource_ids": ["res_ramu"],
                "start_at": "2026-12-15T09:00:00Z",
                "end_at": "2026-12-15T17:00:00Z",
                "ttl_minutes": 30,
            },
            idempotency_key=f"{context['idempotency_key']}_hold_slot",
        ))

    # Check if any tool requires approval
    requires_approval = any(
        tc.tool in ["send_quote", "create_payment_link", "request_owner_approval"]
        for tc in tool_calls
    )

    # Check if escalation needed
    escalation_keywords = ["complaint", "refund", "legal", "urgent", "emergency", "manager", "supervisor"]
    escalation_needed = any(kw in msg_lower for kw in escalation_keywords)

    # Log tool calls to trace
    trace_id = f"trace_{datetime.utcnow().timestamp()}"
    for tc in tool_calls:
        await db.agentTrace.create(
            data={
                "tenantId": tenant_ctx["tenant_id"],
                "conversationId": conversation.id,
                "leadId": conversation.leadId,
                "toolName": tc.tool,
                "inputJson": tc.arguments,
                "outputJson": {"status": "pending"},
                "policyDecision": "approved" if not requires_approval else "requires_approval",
                "latencyMs": 0,
            }
        )

    return AgentConverseResponse(
        response=response_text,
        tool_calls=tool_calls,
        tool_results=[],
        trace_id=trace_id,
        requires_approval=requires_approval,
        escalation_needed=escalation_needed,
    )

@router.post("/execute-tool", response_model=ToolResult)
async def execute_tool(
    tool_call: ToolCall,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Execute a specific tool (called by frontend after user approval)"""
    # Verify tool exists
    if tool_call.tool not in AGENT_TOOLS:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_call.tool}")

    # Execute tool (in production, call actual service)
    # For now, return mock results
    mock_results = {
        "check_availability": {
            "available": True,
            "slots": [
                {"resource": "res_ramu", "start": "2026-12-15T09:00:00Z", "end": "2026-12-15T17:00:00Z"},
                {"resource": "res_adithya", "start": "2026-12-15T09:00:00Z", "end": "2026-12-15T17:00:00Z"},
            ],
        },
        "calculate_quote": {
            "quote_id": f"quote_{datetime.utcnow().timestamp()}",
            "total_paise": 12500000,
            "items": [{"name": "Full Marriage Coverage", "base_paise": 12500000, "quantity": 1}],
        },
        "hold_slot": {
            "hold_id": f"hold_{datetime.utcnow().timestamp()}",
            "expires_at": "2026-12-15T09:30:00Z",
        },
        "send_quote": {"message_id": "msg_123", "status": "sent"},
        "create_payment_link": {"order_id": "order_123", "payment_url": "https://rzp.io/xyz"},
        "request_owner_approval": {"approval_id": "approval_123", "status": "pending"},
        "handoff_to_human": {"escalation_id": "esc_123", "status": "queued"},
    }

    result = mock_results.get(tool_call.tool, {"status": "executed"})

    # Update trace
    await db.agentTrace.update_many(
        where={
            "tenantId": tenant_ctx["tenant_id"],
            "toolName": tool_call.tool,
            "inputJson": tool_call.arguments,
        },
        data={"outputJson": result, "latencyMs": 100},
    )

    return ToolResult(tool=tool_call.tool, success=True, result=result)

@router.get("/traces/{conversation_id}", response_model=List[AgentTraceResponse])
async def get_traces(
    conversation_id: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get agent execution traces for a conversation"""
    traces = await db.agentTrace.find_many(
        where={
            "tenantId": tenant_ctx["tenant_id"],
            "conversationId": conversation_id,
        },
        order={"createdAt": "asc"},
    )
    return [AgentTraceResponse.model_validate(t) for t in traces]

@router.post("/kill-switch")
async def toggle_kill_switch(
    request: KillSwitchRequest,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Enable/disable AI agent for tenant"""
    # Check permissions
    if tenant_ctx["role"] != "studio.owner":
        raise HTTPException(status_code=403, detail="Only studio owner can toggle kill switch")

    # Update business settings
    await db.businessSettings.update(
        where={"tenantId": tenant_ctx["tenant_id"]},
        data={
            "settingsJson": {
                "set": {"ai_agent.enabled": request.enabled},
            }
        },
    )

    # Audit
    await db.auditEvent.create(
        data={
            "tenantId": tenant_ctx["tenant_id"],
            "actorId": tenant_ctx["user_id"],
            "action": "agent_kill_switch_toggled",
            "entityType": "settings",
            "entityId": "ai_agent",
            "beforeAfterRef": {"after": {"enabled": request.enabled, "reason": request.reason}},
        }
    )

    logger.warning("AI agent kill switch toggled", tenant=tenant_ctx["tenant_id"], enabled=request.enabled)
    return {"enabled": request.enabled, "message": f"AI agent {'enabled' if request.enabled else 'disabled'}"}

@router.get("/evaluation")
async def get_evaluation_results(
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get agent evaluation results (for monitoring)"""
    # In production: run evaluation suite and return results
    return {
        "golden_set_pass_rate": 0.95,
        "adversarial_detection_rate": 0.92,
        "avg_latency_ms": 1200,
        "total_conversations_today": 47,
        "escalation_rate": 0.08,
        "tool_call_success_rate": 0.98,
    }