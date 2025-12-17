"""
Jira Refinement Copilot - Version 2
Fixes:
1. Intent misclassification (confidence + multi-intent)
2. Over-structured responses (adaptive style)
3. Hidden assumptions (assumption gate)
"""

# =========================================================
# 1. MASTER META PROMPT
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
# 2. INTENT CLASSIFIER PROMPT (V2)
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
# 3. MODE PROMPTS
# =========================================================

MODE_PROMPTS = {
    "OBJECTIVE_INTENT": "Explain the objective and business purpose.",
    "SCOPE_DEFINITION": "Define in-scope and out-of-scope items.",
    "ACCEPTANCE_CRITERIA": "Generate clear Given/When/Then acceptance criteria.",
    "UI_UX_BEHAVIOUR": "Describe expected UI behaviour and states.",
    "FIGMA_ALIGNMENT": "List Figma design checks for alignment.",
    "EDGE_CASE_RISK_ANALYSIS": "Identify edge cases and risks.",
    "BUSINESS_RULE": "Extract business rules.",
    "DEPENDENCY_IMPACT": "Identify dependencies and impacts.",
    "STORY_REFINEMENT": "Improve clarity and readiness of the requirement.",
    "DEVELOPMENT_READINESS": "Assess if ready for development and list gaps."
}

# =========================================================
# 4. CONTEXT EXTRACTION
# =========================================================

def extract_context(question: str) -> dict:
    q = question.lower()
    return {
        "ui_related": any(w in q for w in ["button", "screen", "click", "field", "page"]),
        "mentions_figma": "figma" in q,
        "mentions_scope": "scope" in q,
        "mentions_ac": any(w in q for w in ["acceptance", "ac"]),
        "mentions_ready": any(w in q for w in ["ready", "sprint", "development"])
    }

# =========================================================
# 5. RESPONSE STYLE DETECTION (NEW)
# =========================================================

def detect_response_style(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["just explain", "in simple terms", "what is"]):
        return "CONVERSATIONAL"
    if any(w in q for w in ["acceptance", "scope", "ready", "criteria"]):
        return "STRUCTURED"
    return "HYBRID"

# =========================================================
# 6. INTENT CLASSIFICATION (V2)
# =========================================================

def classify_intent(llm_classifier, question: str) -> dict:
    prompt = INTENT_CLASSIFIER_PROMPT.format(question=question)
    response = llm_classifier(prompt)

    try:
        import json
        data = json.loads(response)
        return {
            "primary": data.get("primary_intent", "STORY_REFINEMENT"),
            "secondary": data.get("secondary_intents", []),
            "confidence": data.get("confidence", 0.5)
        }
    except Exception:
        return {
            "primary": "STORY_REFINEMENT",
            "secondary": [],
            "confidence": 0.4
        }

# =========================================================
# 7. ASSUMPTION GATE (NEW)
# =========================================================

def assumption_gate(intent: str, context: dict) -> bool:
    """
    Returns True if assumptions are likely required.
    """
    if intent in ["ACCEPTANCE_CRITERIA", "DEVELOPMENT_READINESS"]:
        return not context.get("ui_related", False)
    return False

# =========================================================
# 8. FINAL PROMPT COMPOSER
# =========================================================

def compose_final_prompt(
    master: str,
    mode_prompt: str,
    question: str,
    context: dict,
    style: str,
    require_assumptions: bool
) -> str:

    assumption_instruction = ""
    if require_assumptions:
        assumption_instruction = """
If information is missing:
- List assumptions explicitly
- Ask clarification questions
"""

    return f"""
{master}

Response Style: {style}

Task:
{mode_prompt}

{assumption_instruction}

Context:
{context}

User Question:
{question}
"""

# =========================================================
# 9. MAIN RESPONSE GENERATION
# =========================================================

def generate_response(llm_main, prompt: str) -> str:
    return llm_main(prompt)

# =========================================================
# 10. ORCHESTRATOR (V2 PIPELINE)
# =========================================================

def jira_refinement_copilot_v2(
    llm_classifier,
    llm_main,
    user_question: str
) -> str:

    # Step 1: Context
    context = extract_context(user_question)

    # Step 2: Style
    style = detect_response_style(user_question)

    # Step 3: Intent classification
    intent_data = classify_intent(llm_classifier, user_question)
    primary_intent = intent_data["primary"]
    confidence = intent_data["confidence"]
    secondary_intents = intent_data["secondary"]

    # Step 4: Low confidence → clarify
    if confidence < 0.6:
        return (
            "I need a bit more clarity before answering.\n\n"
            "Could you please confirm what you want to focus on:\n"
            "- Objective\n- Scope\n- Acceptance Criteria\n- Readiness for development?"
        )

    # Step 5: Assumption gate
    needs_assumptions = assumption_gate(primary_intent, context)

    # Step 6: Prompt composition
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

    return response

# =========================================================
# 11. EXAMPLE USAGE
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