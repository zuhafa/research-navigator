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
from pydantic import BaseModel, Field

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from .config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResearchNavigator")

# =====================================================================
# Pydantic Schemas for Consolidated Sub-Agents
# =====================================================================

class PaperSummary(BaseModel):
    objective: str = Field(description="The core objective or goal of the research.")
    methodology: str = Field(description="The methods, models, or algorithms used.")
    dataset_name: str = Field(description="The primary dataset used in the paper.")
    results: str = Field(description="The key findings or metrics achieved.")
    limitations: str = Field(description="Any limitations or drawbacks of the research.")

class PrerequisitesAndLearningPath(BaseModel):
    required_knowledge: list[str] = Field(description="List of specific prerequisite topics required.")
    estimated_learning_time_weeks: int = Field(description="Estimated weeks needed for a beginner to learn these prerequisites.")
    details: str = Field(description="Additional learning recommendations or resource suggestions.")
    week_1: list[str] = Field(description="Topics/tasks to learn in week 1.")
    week_2: list[str] = Field(description="Topics/tasks to learn in week 2.")
    week_3: list[str] = Field(description="Topics/tasks to learn in week 3.")
    week_4: list[str] = Field(description="Topics/tasks to learn in week 4.")
    learning_sequence: str = Field(description="Summary of the overall personalized learning sequence.")

class ImplementationDatasetImpact(BaseModel):
    difficulty: str = Field(description="Complexity level (e.g. Easy, Intermediate, Hard).")
    required_tools: list[str] = Field(description="Key tools, frameworks, and libraries needed.")
    hardware: str = Field(description="Hardware suggestions (e.g. CPU, GPU recommended, TPU).")
    build_time_weeks: int = Field(description="Estimated implementation duration in weeks.")
    dataset_name: str = Field(description="Name of the main dataset.")
    dataset_size: str = Field(description="Approximate size or number of samples.")
    dataset_access: str = Field(description="Access status (e.g. Public, Kaggle, Restricted).")
    dataset_difficulty: str = Field(description="Difficulty level of dataset preprocessing/handling.")
    dataset_alternatives: list[str] = Field(description="List of alternative datasets in the same domain.")
    real_world_applications: list[str] = Field(description="Real-world applications of this research.")
    industry_relevance: str = Field(description="Evaluation of industry relevance (e.g. High, Medium, Low).")
    societal_impact: str = Field(description="Societal impact and benefits.")
    future_opportunities: list[str] = Field(description="Future opportunities or research directions.")

class ProjectIdeas(BaseModel):
    beginner: str = Field(description="Beginner project idea and brief path.")
    intermediate: str = Field(description="Intermediate project idea and brief path.")
    advanced: str = Field(description="Advanced project idea and brief path.")

class MentorshipReadinessFeasibility(BaseModel):
    readiness_score: int = Field(description="Readiness evaluation score between 0 and 100.")
    skill_level: str = Field(description="Evaluated skill level (Beginner/Intermediate/Advanced).")
    feasibility_level: str = Field(description="Feasibility grade (Low / Medium / High).")
    can_understand: bool = Field(description="Can this user realistically understand this paper?")
    can_implement: bool = Field(description="Can this user realistically implement this paper?")
    suitability: str = Field(description="Suitability recommendation grade (e.g. Recommended, Not Recommended Yet).")
    missing_skills: list[str] = Field(description="List of key missing skills user needs to learn.")
    recommended_prep_weeks: int = Field(description="Suggested prep time before starting in weeks.")
    reasoning: str = Field(description="Explainable feasibility reasoning, justification, and final next steps recommendation.")

# =====================================================================
# Specialized Sub-Agents Definitions
# =====================================================================

# Create connection params to the local MCP server
mcp_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="python",
        args=["app/mcp_server.py"]
    )
)

# Create Toolsets for the agents
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

paper_analyzer = LlmAgent(
    name="paper_analyzer",
    model=Gemini(model=config.model),
    instruction="""You are a Research Paper Analysis Agent.
Analyze the user's research input (a paper name, abstract, URL, or topic).
Summarize the research objectives, methodology, main dataset used, results, and limitations.
Return structured JSON output matching the PaperSummary schema.""",
    output_schema=PaperSummary,
    output_key="paper_summary",
    description="Summarizes research objectives, methodology, datasets, results, and limitations from a research input query."
)

prerequisite_and_learning_path_analyzer = LlmAgent(
    name="prerequisite_and_learning_path_analyzer",
    model=Gemini(model=config.model),
    instruction="""You are the Prerequisite and Learning Path Analyzer.
Determine the required prerequisite knowledge (e.g. languages, math, deep learning concepts) for the paper or topic.
You must fetch learning path details to generate a personalized weekly learning path (Week 1 to 4).
You must query both the check_prerequisites tool and the get_learning_path tool.
Return structured JSON output matching the PrerequisitesAndLearningPath schema.""",
    output_schema=PrerequisitesAndLearningPath,
    output_key="prerequisites_and_learning_path",
    tools=[prereq_mcp, learning_path_mcp],
    description="Determines required prerequisite knowledge, learning topics, and constructs a personalized weekly roadmap."
)

implementation_dataset_impact_analyzer = LlmAgent(
    name="implementation_dataset_impact_analyzer",
    model=Gemini(model=config.model),
    instruction="""You are the Implementation, Dataset, and Research Impact Analyzer.
Evaluate the implementation difficulty (Easy, Intermediate, Hard), tools/libraries, hardware requirements, and build time.
Identify dataset details (name, size, accessibility, difficulty, and alternatives).
Determine real-world applications, industry relevance, societal impact, and future opportunities.
You must query the estimate_complexity, check_dataset_spec, and get_research_domain tools to fetch detailed groundings.
Return structured JSON output matching the ImplementationDatasetImpact schema.""",
    output_schema=ImplementationDatasetImpact,
    output_key="implementation_dataset_impact",
    tools=[impl_mcp, dataset_mcp, impact_mcp],
    description="Evaluates build difficulty, tools, hardware, dataset specifications, alternatives, and research domain impact."
)

project_idea_generator = LlmAgent(
    name="project_idea_generator",
    model=Gemini(model=config.model),
    instruction="""You are a Project Idea Agent.
Propose three project ideas based on the research paper or topic:
- Beginner level project
- Intermediate level project
- Advanced level project
Return structured JSON output matching the ProjectIdeas schema.""",
    output_schema=ProjectIdeas,
    output_key="project_ideas",
    description="Generates beginner, intermediate, and advanced practical project ideas based on the research."
)

readiness_and_feasibility_mentor = LlmAgent(
    name="readiness_and_feasibility_mentor",
    model=Gemini(model=config.model),
    instruction="""You are the Readiness, Feasibility, and Research Mentorship Agent.
Evaluate overall user suitability (default: Beginner) to pursue this research project.
Determine user readiness score (0-100), skill level, feasibility level (Low/Medium/High), missing skills, suggested prep time, and next actions.
You must query get_readiness_rules and get_project_templates tools to obtain skill weightings and reference templates.
Use explainable reasoning and do not output random scores.
Return structured JSON output matching the MentorshipReadinessFeasibility schema.""",
    output_schema=MentorshipReadinessFeasibility,
    output_key="readiness_feasibility_mentorship",
    tools=[readiness_mcp, feasibility_mcp],
    description="Performs user readiness assessment, checks feasibility, and gives final next-steps preparation plan."
)

# =====================================================================
# Coordinator Agent Definition
# =====================================================================

orchestrator_instruction = """You are the Coordinator for the Research Navigator AI.
Your task is to analyze the research paper input, abstract, topic, or arXiv URL provided by the user.
To perform this task, you MUST invoke all of the following specialized sub-agents in order:
1. Call paper_analyzer to summarize the paper.
2. Call prerequisite_and_learning_path_analyzer to determine prerequisites and build the learning path.
3. Call implementation_dataset_impact_analyzer to evaluate complexity, datasets, and research impact.
4. Call project_idea_generator to generate project ideas.
5. Call readiness_and_feasibility_mentor to assess readiness, feasibility, and mentorship recommendations.

After collecting all the outputs, combine them into a single comprehensive markdown report.
Your final response MUST be a detailed, structured markdown report containing:
- Executive Summary of the Paper (from paper_analyzer)
- Prerequisite Analysis & Required Skills (from prerequisite_and_learning_path_analyzer)
- Dataset Details & Alternatives (from implementation_dataset_impact_analyzer)
- Implementation & Tools Complexity Assessment (from implementation_dataset_impact_analyzer)
- Research Readiness Evaluation (from readiness_and_feasibility_mentor)
- Weekly Personalized Learning Plan (from prerequisite_and_learning_path_analyzer)
- Research Feasibility Assessment (from readiness_and_feasibility_mentor)
- Suggested Project Templates & Ideas (from project_idea_generator)
- Real-World Research Impact & Industry Relevance (from implementation_dataset_impact_analyzer)
- Final Research Mentor Suitability Recommendation (from readiness_and_feasibility_mentor)

Ensure you present the findings clearly.
Original Query: {query}
Feedback from User (if any): {feedback}"""

# Global lock to serialize sub-agent execution
tool_lock = asyncio.Lock()

async def serialize_tool_calls(tool: Any, args: dict, tool_context: ToolContext) -> None:
    """Forces parallel tool calls to run sequentially to avoid 503/429 rate limit spikes on Gemini API."""
    async with tool_lock:
        logger.info(f"Lock acquired. Space out API execution: running {tool.name}")
        await asyncio.sleep(12.5)  # 12.5s delay to space out API calls and stay under 5 RPM free tier limit
        return None

orchestrator = LlmAgent(
    name="orchestrator",
    model=Gemini(model=config.model),
    instruction=orchestrator_instruction,
    tools=[
        AgentTool(paper_analyzer),
        AgentTool(prerequisite_and_learning_path_analyzer),
        AgentTool(implementation_dataset_impact_analyzer),
        AgentTool(project_idea_generator),
        AgentTool(readiness_and_feasibility_mentor),
    ],
    before_tool_callback=serialize_tool_calls,
    description="The main coordinator that delegates tasks to specialist sub-agents and produces a consolidated report."
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
