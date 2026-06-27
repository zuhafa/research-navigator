import os
import re
import datetime
import json
import logging
import asyncio
from typing import AsyncGenerator, Any

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import AgentTool, ToolContext
from google.adk.apps import App, ResumabilityConfig
from google.adk.models import Gemini
from google.adk.workflow import Workflow, START, node
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from .config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResearchNavigator")

# =====================================================================
# Local MCP Toolsets Definition
# =====================================================================

# Create connection params to the local MCP server
mcp_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="python",
        args=["app/mcp_server.py"]
    )
)

# Create Toolsets for direct coordinator grounding
prereq_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["check_prerequisites"]
)

dataset_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["check_dataset_spec"]
)

impl_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["estimate_complexity"]
)

readiness_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["get_readiness_rules"]
)

learning_path_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["get_learning_path"]
)

feasibility_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["get_project_templates"]
)

impact_mcp = McpToolset(
    connection_params=mcp_connection,
    tool_filter=["get_research_domain"]
)

# =====================================================================
# Coordinator Agent Definition
# =====================================================================

orchestrator_instruction = """You are the Research Mentor Coordinator for the Research Navigator AI.
Your task is to analyze the research paper input, abstract, topic, or arXiv URL provided by the user.

To perform this analysis, you must query all of the following local MCP tools to retrieve grounded roadmap context:
1. Call get_research_domain with the topic to classify domain, subfield, difficulty, and relevance.
2. Call check_prerequisites to determine the prerequisite knowledge required.
3. Call get_learning_path to obtain a structured weekly roadmap.
4. Call estimate_complexity to assess library dependencies and implementation time.
5. Call check_dataset_spec to query data specs, size, accessibility, and alternatives.
6. Call get_readiness_rules to retrieve readiness skill evaluation weights.
7. Call get_project_templates to get reference template project ideas.

After fetching the grounded data from these local tools, analyze it and generate a single comprehensive, structured markdown mentorship report.
Your response MUST contain the following 10 sections:
- **Executive Summary**: Core objectives, methodology, key findings, and limitations.
- **Prerequisite Analysis**: Specific prerequisite topics and skills required.
- **Dataset Details & Alternatives**: Specifications, sizes, accessibility, and alternative public options.
- **Complexity Assessment**: Build difficulty, libraries, hardware recommendations, and estimated weeks.
- **Research Readiness Score**: Calculate a readiness score (0-100) using retrieved weightings. Explain your calculation.
- **Weekly Learning Plan**: Personalized Week 1 to 4 preparation schedule.
- **Research Feasibility**: Determine suitability level (Low/Medium/High) and justify in plain English.
- **Suggested Projects**: Beginner, intermediate, and advanced practical project templates.
- **Research Impact**: Real-world applications, industry relevance, and societal benefits.
- **Mentor Suitability Recommendation**: Evaluated user level, suitability grade, missing skills, recommended prep time, and next actions.

Ensure you present the findings clearly.
Original Query: {query}
Feedback from User (if any): {feedback}"""

orchestrator = LlmAgent(
    name="orchestrator",
    model=Gemini(
        model=config.model,
        retry_options=types.HttpRetryOptions(
            attempts=6,
            initial_delay=2.0,
            max_delay=8.0,
            http_status_codes=[429, 503, 504]
        )
    ),
    instruction=orchestrator_instruction,
    tools=[
        prereq_mcp,
        dataset_mcp,
        impl_mcp,
        readiness_mcp,
        learning_path_mcp,
        feasibility_mcp,
        impact_mcp,
    ],
    description="The main research mentor that queries local MCP tools and synthesizes a comprehensive report in a single turn."
)

# =====================================================================
# Helper and Node Functions
# =====================================================================

def extract_text(content: types.Content) -> str:
    """Helper to safely extract text from types.Content object."""
    if not content or not content.parts:
        return ""
    return "".join(part.text for part in content.parts if part.text)

def log_audit(severity: str, action: str, details: dict):
    """Logs structured JSON audit log."""
    log_data = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "severity": severity,
        "action": action,
        "details": details
    }
    logger.info(f"AUDIT_LOG: {json.dumps(log_data)}")

async def init_state_callback(callback_context: CallbackContext) -> None:
    """Callback to initialize context state before agent starts."""
    if "query" not in callback_context.state:
        callback_context.state["query"] = ""
    if "feedback" not in callback_context.state:
        callback_context.state["feedback"] = "No feedback yet."

# Configure orchestrator callback
orchestrator.before_agent_callback = init_state_callback

# =====================================================================
# Workflow Graph Nodes
# =====================================================================

def security_checkpoint(ctx: Context, node_input: types.Content):
    """Validates the input query, checks for prompt injection, scrubs PII, and logs details."""
    raw_text = extract_text(node_input)
    
    # 1. PII Scrubbing
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    
    clean_text = raw_text
    emails_found = re.findall(email_pattern, raw_text)
    phones_found = re.findall(phone_pattern, raw_text)
    
    if emails_found or phones_found:
        clean_text = re.sub(email_pattern, "[REDACTED_EMAIL]", clean_text)
        clean_text = re.sub(phone_pattern, "[REDACTED_PHONE]", clean_text)
        log_audit("WARNING", "PII_REDACTION", {"emails_count": len(emails_found), "phones_count": len(phones_found)})

    # 2. Shell/System Execution Block
    exec_patterns = [
        r"os\.system\b",
        r"subprocess\b",
        r"exec\s*\(",
        r"eval\s*\(",
        r"rm\s+-rf\b",
        r"\|\s*sh\b",
        r"\|\s*bash\b",
        r"sh\s+-c\b",
        r"bash\s+-c\b"
    ]
    exec_detected = any(re.search(pat, raw_text) for pat in exec_patterns)
    if exec_detected:
        log_audit("CRITICAL", "SHELL_EXECUTION_ATTEMPT_DETECTED", {"query_snippet": raw_text[:100]})
        return Event(
            output="Execution attempt detected. Shell or system execution queries are blocked.",
            route="fail"
        )

    # 3. Prompt Injection Detection
    injection_keywords = [
        "ignore previous instructions",
        "system prompt",
        "ignore all guidelines",
        "bypass security",
        "you are now an admin"
    ]
    injection_detected = any(kw in clean_text.lower() for kw in injection_keywords)
    
    if injection_detected:
        log_audit("CRITICAL", "PROMPT_INJECTION_DETECTED", {"query_snippet": clean_text[:100]})
        return Event(
            output="Prompt injection attempt detected.",
            route="fail"
        )

    # 4. Domain-Specific Verification (Must look like academic, paper, URL or topic query)
    academic_keywords = [
        "paper", "arxiv", "abstract", "study", "research", "dataset", "learning", 
        "classification", "transformer", "network", "algorithm", "model", "imaging", 
        "mri", "medical", "cnn", "attention", "nlp", "bert", "gpt", "segmentation", "science"
    ]
    is_url = "http" in clean_text.lower() or "arxiv.org" in clean_text.lower() or ".pdf" in clean_text.lower()
    has_academic_term = any(term in clean_text.lower() for term in academic_keywords)
    
    if not (is_url or has_academic_term or len(clean_text) > 15):
        log_audit("INFO", "OUT_OF_DOMAIN_INPUT", {"input": clean_text})
        return Event(
            output="Your query does not seem to relate to academic research papers, concepts, or datasets. Please query about a research topic, paper abstract, URL, or dataset.",
            route="fail"
        )

    # Save clean query to state for orchestrator injection
    log_audit("INFO", "INPUT_CLEANED_AND_APPROVED", {"input_length": len(clean_text)})
    
    # Wrap back to Content
    cleaned_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=clean_text)]
    )
    
    return Event(
        output=cleaned_content,
        route="pass",
        state={"query": clean_text}
    )

def security_alert(node_input: str):
    """Node that handles security/domain rejection errors and returns standard message."""
    yield Event(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=f"⚠️ **Security Checkpoint Flagged:** {node_input}")]
        )
    )
    yield Event(output={"error": node_input})

async def human_review(ctx: Context, node_input: types.Content):
    """Waits for human in the loop input before completing the workflow."""
    report_text = extract_text(node_input)
    
    # If the report is non-empty, cache it in state
    if report_text:
        ctx.state["pending_report"] = report_text
    
    cached_report = ctx.state.get("pending_report", "")

    if not ctx.resume_inputs or "approval" not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id="approval",
            message="📋 Please review the generated research report. Reply 'approve' to finalize, or type your feedback to adjust."
        )
        return

    user_response = ctx.resume_inputs["approval"]
    if user_response.strip().lower() == "approve":
        log_audit("INFO", "REPORT_APPROVED", {})
        yield Event(output=cached_report, route="approve")
    else:
        log_audit("INFO", "REPORT_REJECTED_WITH_FEEDBACK", {"feedback": user_response})
        yield Event(
            output=cleaned_feedback_content(user_response),
            route="reject",
            state={"feedback": user_response}
        )

def cleaned_feedback_content(feedback_text: str) -> types.Content:
    """Wraps user feedback in Content structure."""
    return types.Content(
        role="user",
        parts=[types.Part.from_text(text=f"Adjust report based on human feedback: {feedback_text}")]
    )

def final_report(node_input: str):
    """Outputs the finalized approved report to the user."""
    yield Event(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=f"🎉 **Final Approved Report:**\n\n{node_input}")]
        )
    )
    yield Event(output={"report": node_input})

# =====================================================================
# ADK 2.0 Graph Workflow Definition
# =====================================================================

root_agent = Workflow(
    name="research_navigator_workflow",
    edges=[
        (START, security_checkpoint),
        
        # Security paths
        (security_checkpoint, {"pass": orchestrator, "fail": security_alert}),
        
        # Main orchestrator -> review loop
        (orchestrator, human_review),
        
        # Human review outputs
        (human_review, {"approve": final_report, "reject": orchestrator})
    ],
    description="Research Navigator workflow that filters input, coordinates specialized sub-agents, and runs a human review check."
)

app = App(
    name="app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
