"""
Jira Refinement Copilot - Version 2
Fixes:
1. Intent misclassification (confidence + multi-intent)
2. Over-structured responses (adaptive style)
3. Hidden assumptions (assumption gate)

Enhancements (V2.1):
4. Dynamic thresholds per intent type
5. Intent-specific clarifying questions
6. Structured error handling with logging
7. Enhanced context-aware responses
8. Modular, testable components
"""

import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================================================
# 1. CONFIGURATION: DYNAMIC THRESHOLDS
# =========================================================

INTENT_THRESHOLDS = {
    "OBJECTIVE_INTENT": 0.7,
    "SCOPE_DEFINITION": 0.65,
    "ACCEPTANCE_CRITERIA": 0.6,
    "UI_UX_BEHAVIOUR": 0.6,
    "FIGMA_ALIGNMENT": 0.65,
    "EDGE_CASE_RISK_ANALYSIS": 0.5,  # Lower for nuanced analysis
    "BUSINESS_RULE": 0.6,
    "DEPENDENCY_IMPACT": 0.55,
    "STORY_REFINEMENT": 0.5,  # Lower for general refinement
    "DEVELOPMENT_READINESS": 0.6
}

# =========================================================
# 2. INTENT-SPECIFIC CLARIFYING QUESTIONS
# =========================================================

CLARIFYING_QUESTIONS = {
    "OBJECTIVE_INTENT": (
        "I need a bit more clarity. Could you specify:\n"
        "- What business goal does this feature support?\n"
        "- Who are the primary users?\n"
        "- What problem does this solve?"
    ),
    "SCOPE_DEFINITION": (
        "To define the scope clearly, please clarify:\n"
        "- What functionality is included?\n"
        "- What is explicitly out of scope?\n"
        "- Are there any phase requirements?"
    ),
    "ACCEPTANCE_CRITERIA": (
        "To create clear acceptance criteria, I need:\n"
        "- What are the specific conditions to be met?\n"
        "- What are the expected outcomes?\n"
        "- Are there UI/UX or data validation requirements?"
    ),
    "UI_UX_BEHAVIOUR": (
        "For UI/UX behavior, please specify:\n"
        "- What user actions trigger this behavior?\n"
        "- What visual feedback should users see?\n"
        "- Are there error or loading states?"
    ),
    "FIGMA_ALIGNMENT": (
        "To ensure Figma alignment, I need:\n"
        "- Which Figma design/mockup should be referenced?\n"
        "- Are there specific components or flows to validate?\n"
        "- Are there any design system requirements?"
    ),
    "EDGE_CASE_RISK_ANALYSIS": (
        "For edge case analysis, help me understand:\n"
        "- What are the expected normal conditions?\n"
        "- What unusual inputs or scenarios concern you?\n"
        "- Are there integration or data quality risks?"
    ),
    "BUSINESS_RULE": (
        "To extract business rules clearly:\n"
        "- What conditions must be met?\n"
        "- What are the validation requirements?\n"
        "- Are there any exceptions or special cases?"
    ),
    "DEPENDENCY_IMPACT": (
        "To identify dependencies, clarify:\n"
        "- What other systems or features are affected?\n"
        "- Are there API or data dependencies?\n"
        "- What's the impact on existing functionality?"
    ),
    "STORY_REFINEMENT": (
        "To refine this story, I need more context:\n"
        "- What aspect needs refinement (clarity, completeness, readiness)?\n"
        "- Are there specific concerns or gaps?\n"
        "- What level of detail is needed?"
    ),
    "DEVELOPMENT_READINESS": (
        "To assess development readiness:\n"
        "- Have all dependencies been identified?\n"
        "- Are acceptance criteria defined?\n"
        "- Are there any open questions or blockers?"
    )
}

# =========================================================
# 3. MASTER META PROMPT
# =========================================================

MASTER_PROMPT = """
You are a Senior Business Analyst, Product Owner, and Jira Coach assistant.

Your role is to help refine Jira tickets by analysing:
- Business intent
- Functional scope
- UI/UX behaviour (including Figma expectations)
- Acceptance criteria
- Edge cases, risks, and dependencies

Rules:
- Understand the user's intent first.
- Adapt response style based on the question.
- Do NOT assume missing requirements.
- Clearly list assumptions when information is missing.
- Ask clarification questions when needed.
- Provide Jira-ready, practical outputs.

You are a thinking partner, not a decision authority.
"""

# =========================================================
# 4. INTENT CLASSIFIER PROMPT (V2)
# =========================================================

INTENT_CLASSIFIER_PROMPT = """
You are an intent classifier for a Jira Refinement Copilot.

Identify:
- Primary intent
- Secondary intents (if any)
- Confidence score (0.0 to 1.0)

Return JSON ONLY.

Possible intents:
OBJECTIVE_INTENT
SCOPE_DEFINITION
ACCEPTANCE_CRITERIA
UI_UX_BEHAVIOUR
FIGMA_ALIGNMENT
EDGE_CASE_RISK_ANALYSIS
BUSINESS_RULE
DEPENDENCY_IMPACT
STORY_REFINEMENT
DEVELOPMENT_READINESS

User Question:
{question}
"""

# =========================================================
# 5. MODE PROMPTS WITH EXAMPLES AND TEMPLATES
# =========================================================

MODE_PROMPTS = {
    "OBJECTIVE_INTENT": (
        "Explain the objective and business purpose.\n"
        "Focus on: WHY this feature exists, WHO benefits, and WHAT problem it solves."
    ),
    "SCOPE_DEFINITION": (
        "Define in-scope and out-of-scope items.\n"
        "Structure: IN SCOPE (what's included), OUT OF SCOPE (what's excluded), "
        "ASSUMPTIONS (what's assumed but unconfirmed)."
    ),
    "ACCEPTANCE_CRITERIA": (
        "Generate clear Given/When/Then acceptance criteria.\n\n"
        "Template:\n"
        "- GIVEN [precondition/context]\n"
        "- WHEN [action/trigger]\n"
        "- THEN [expected outcome]\n\n"
        "Example:\n"
        "- GIVEN a user is on the login page\n"
        "- WHEN they enter valid credentials and click 'Login'\n"
        "- THEN they should be redirected to the dashboard"
    ),
    "UI_UX_BEHAVIOUR": (
        "Describe expected UI behaviour and states.\n"
        "Include: Default state, Loading state, Success state, Error state, "
        "Edge cases (empty, disabled, etc.)"
    ),
    "FIGMA_ALIGNMENT": (
        "List Figma design checks for alignment.\n"
        "Verify: Component spacing, Typography, Colors, Icons, "
        "Interaction states (hover, active, disabled), Responsive behavior"
    ),
    "EDGE_CASE_RISK_ANALYSIS": (
        "Identify edge cases and risks.\n"
        "Consider: Invalid inputs, Boundary conditions, System failures, "
        "Integration issues, Performance constraints, Security vulnerabilities"
    ),
    "BUSINESS_RULE": (
        "Extract business rules.\n"
        "Format: IF [condition] THEN [action/outcome] ELSE [alternative]"
    ),
    "DEPENDENCY_IMPACT": (
        "Identify dependencies and impacts.\n"
        "Categories: System dependencies, Data dependencies, "
        "Feature dependencies, API dependencies, Impact on existing features"
    ),
    "STORY_REFINEMENT": (
        "Improve clarity and readiness of the requirement.\n"
        "Check: Clear objective, Defined scope, Acceptance criteria, "
        "Dependencies identified, Assumptions documented"
    ),
    "DEVELOPMENT_READINESS": (
        "Assess if ready for development and list gaps.\n"
        "Checklist: ✓/✗ Clear requirements, ✓/✗ Acceptance criteria defined, "
        "✓/✗ Dependencies identified, ✓/✗ Designs available, ✓/✗ Technical approach agreed"
    )
}

# =========================================================
# 6. CONTEXT EXTRACTION (ENHANCED)
# =========================================================

def extract_context(question: str) -> dict:
    """
    Dynamically extract context from the user's question.
    
    Args:
        question: User's input question
        
    Returns:
        Dictionary with context flags and metadata
    """
    q = question.lower()
    
    context = {
        "ui_related": any(w in q for w in ["button", "screen", "click", "field", "page", "form", "input", "modal", "popup"]),
        "mentions_figma": "figma" in q or "mockup" in q or "design mockup" in q or "ui design" in q,
        "mentions_scope": "scope" in q or "in-scope" in q or "out of scope" in q,
        "mentions_ac": any(w in q for w in ["acceptance", "ac", "criteria"]),
        "mentions_ready": any(w in q for w in ["ready", "sprint", "development"]),
        "mentions_edge_cases": any(w in q for w in ["edge", "risk", "error", "failure", "exception"]),
        "mentions_business_rules": any(w in q for w in ["rule", "validation", "condition"]) or "if then" in q or "if-then" in q,
        "has_question_words": any(w in q for w in ["what", "why", "how", "when", "where", "who"])
    }
    
    # Log extracted context for debugging
    logger.debug(f"Extracted context: {context}")
    
    return context

# =========================================================
# 7. RESPONSE STYLE DETECTION (ENHANCED)
# =========================================================

def detect_response_style(question: str) -> str:
    """
    Detect the appropriate response style based on the question.
    
    Args:
        question: User's input question
        
    Returns:
        Response style: CONVERSATIONAL, STRUCTURED, or HYBRID
    """
    q = question.lower()
    
    # Conversational indicators
    if any(w in q for w in ["just explain", "in simple terms", "what is", "why", "help me understand"]):
        style = "CONVERSATIONAL"
    # Structured indicators
    elif any(w in q for w in ["acceptance", "scope", "ready", "criteria", "list", "define"]):
        style = "STRUCTURED"
    else:
        style = "HYBRID"
    
    logger.debug(f"Detected response style: {style}")
    return style

# =========================================================
# 8. INTENT CLASSIFICATION (V2 - ENHANCED)
# =========================================================

def classify_intent(llm_classifier, question: str) -> dict:
    """
    Classify the user's intent with confidence scoring.
    
    Args:
        llm_classifier: LLM function for classification
        question: User's input question
        
    Returns:
        Dictionary with primary intent, secondary intents, and confidence
    """
    prompt = INTENT_CLASSIFIER_PROMPT.format(question=question)
    
    try:
        response = llm_classifier(prompt)
        data = json.loads(response)
        
        result = {
            "primary": data.get("primary_intent", "STORY_REFINEMENT"),
            "secondary": data.get("secondary_intents", []),
            "confidence": data.get("confidence", 0.5)
        }
        
        logger.info(f"Intent classified: {result['primary']} (confidence: {result['confidence']:.2f})")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Raw response: {response[:200]}")
        return {
            "primary": "STORY_REFINEMENT",
            "secondary": [],
            "confidence": 0.4
        }
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return {
            "primary": "STORY_REFINEMENT",
            "secondary": [],
            "confidence": 0.3
        }

# =========================================================
# 9. ASSUMPTION GATE (ENHANCED)
# =========================================================

def assumption_gate(intent: str, context: dict) -> bool:
    """
    Determine if assumptions are likely required for the given intent and context.
    
    Args:
        intent: Primary intent
        context: Extracted context dictionary
        
    Returns:
        True if assumptions are needed, False otherwise
    """
    # High assumption needs for certain intents without sufficient context
    if intent in ["ACCEPTANCE_CRITERIA", "DEVELOPMENT_READINESS"]:
        return not context.get("ui_related", False)
    
    # Figma alignment needs assumptions if design isn't mentioned
    if intent == "FIGMA_ALIGNMENT":
        return not context.get("mentions_figma", False)
    
    # Scope definition needs assumptions if scope isn't clearly stated
    if intent == "SCOPE_DEFINITION":
        return not context.get("mentions_scope", False)
    
    return False

# =========================================================
# 10. FINAL PROMPT COMPOSER (CONTEXT-AWARE)
# =========================================================

def compose_final_prompt(
    master: str,
    mode_prompt: str,
    question: str,
    context: dict,
    style: str,
    require_assumptions: bool
) -> str:
    """
    Compose the final prompt with context-aware instructions.
    
    Args:
        master: Master prompt template
        mode_prompt: Intent-specific prompt
        question: User's question
        context: Extracted context
        style: Response style
        require_assumptions: Whether to ask for assumptions
        
    Returns:
        Composed final prompt string
    """
    
    assumption_instruction = ""
    if require_assumptions:
        assumption_instruction = """
If information is missing:
- List assumptions explicitly
- Ask clarification questions
"""
    
    # Add context-specific instructions
    context_instructions = ""
    if context.get("mentions_figma"):
        context_instructions += "\n⚠️ IMPORTANT: User mentioned Figma. Emphasize design alignment checks and verify against Figma mockups."
    
    if context.get("ui_related") and not context.get("mentions_figma"):
        context_instructions += "\n⚠️ NOTE: This is UI-related. Consider suggesting Figma validation if designs exist."
    
    if context.get("mentions_edge_cases"):
        context_instructions += "\n⚠️ FOCUS: User is concerned about edge cases. Provide comprehensive risk analysis."
    
    return f"""
{master}

Response Style: {style}

Task:
{mode_prompt}

{assumption_instruction}
{context_instructions}

Context Extracted:
{context}

User Question:
{question}
"""

# =========================================================
# 11. MAIN RESPONSE GENERATION (WITH ERROR HANDLING)
# =========================================================

def generate_response(llm_main, prompt: str) -> str:
    """
    Generate response from the main LLM with error handling.
    
    Args:
        llm_main: Main LLM function
        prompt: Composed prompt
        
    Returns:
        Generated response string
    """
    try:
        response = llm_main(prompt)
        logger.info("Response generated successfully")
        return response
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return (
            "I apologize, but I encountered an error generating the response. "
            "Please try rephrasing your question or contact support if the issue persists."
        )

# =========================================================
# 12. ORCHESTRATOR (V2.1 PIPELINE - ENHANCED)
# =========================================================

def jira_refinement_copilot_v2(
    llm_classifier,
    llm_main,
    user_question: str
) -> str:
    """
    Main orchestrator for the Jira Refinement Copilot.
    
    Args:
        llm_classifier: LLM for intent classification
        llm_main: Main LLM for response generation
        user_question: User's input question
        
    Returns:
        Generated response string
    """
    
    try:
        logger.info(f"Processing question: {user_question[:100]}...")
        
        # Step 1: Context extraction
        context = extract_context(user_question)
        
        # Step 2: Response style detection
        style = detect_response_style(user_question)
        
        # Step 3: Intent classification
        intent_data = classify_intent(llm_classifier, user_question)
        primary_intent = intent_data["primary"]
        confidence = intent_data["confidence"]
        secondary_intents = intent_data["secondary"]
        
        # Step 4: Dynamic threshold check based on intent type
        threshold = INTENT_THRESHOLDS.get(primary_intent, 0.6)
        if confidence < threshold:
            logger.warning(f"Low confidence ({confidence:.2f}) below threshold ({threshold})")
            # Return intent-specific clarifying question
            return CLARIFYING_QUESTIONS.get(
                primary_intent,
                CLARIFYING_QUESTIONS["STORY_REFINEMENT"]
            )
        
        # Step 5: Assumption gate
        needs_assumptions = assumption_gate(primary_intent, context)
        
        # Step 6: Prompt composition with context-aware enhancements
        final_prompt = compose_final_prompt(
            MASTER_PROMPT,
            MODE_PROMPTS.get(primary_intent, MODE_PROMPTS["STORY_REFINEMENT"]),
            user_question,
            context,
            style,
            needs_assumptions
        )
        
        # Step 7: Generate response
        response = generate_response(llm_main, final_prompt).strip()
        
        # Step 8: Offer secondary intents
        if secondary_intents:
            response += (
                "\n\nWould you also like help with: "
                + ", ".join(secondary_intents) + "?"
            )
        
        logger.info("Successfully generated response")
        return response
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return (
            "I apologize, but I encountered an unexpected error processing your request. "
            "Please try rephrasing your question or contact support if the issue persists."
        )

# =========================================================
# 13. EXAMPLE USAGE
# =========================================================
"""
def llm_classifier(prompt):
    return '''
    {
      "primary_intent": "OBJECTIVE_INTENT",
      "secondary_intents": [],
      "confidence": 0.85
    }
    '''

def llm_main(prompt):
    return "Objective: The submit button initiates a secure password recovery flow."

print(
    jira_refinement_copilot_v2(
        llm_classifier,
        llm_main,
        "What is the objective of forgot password submit button click?"
    )
)
"""


import re

def format_for_jira_rich_text(text: str) -> str:
    """
    Formats LLM-generated text into clean, readable plain text
    suitable for Jira rich text editor (no markdown, no wiki syntax).
    """

    # Normalize whitespace
    text = text.replace("\r", "").strip()

    lines = text.split("\n")
    output = []
    buffer = ""

    for line in lines:
        line = line.strip()

        # Skip empty lines but flush buffer
        if not line:
            if buffer:
                output.append(buffer.strip())
                buffer = ""
            continue

        # Detect numbered section headings like:
        # 1. **Understanding the Feature**:
        section_match = re.match(r"^\d+\.\s+\*{0,2}(.+?)\*{0,2}:", line)
        if section_match:
            if buffer:
                output.append(buffer.strip())
                buffer = ""
            output.append(f"{section_match.group(1)}:")
            continue

        # Bullet points
        if line.startswith("-"):
            if buffer:
                output.append(buffer.strip())
                buffer = ""
            output.append(line)
            continue

        # Normal text → merge into paragraph
        buffer += " " + line

    if buffer:
        output.append(buffer.strip())

    # Final cleanup
    formatted = "\n".join(output)
    formatted = re.sub(r"\s{2,}", " ", formatted)

    return formatted