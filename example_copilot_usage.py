#!/usr/bin/env python3
"""
Example usage of the Jira Refinement Copilot V2.1

This script demonstrates how to use the refactored copilot with mock LLMs.
In a real implementation, replace the mock functions with actual LLM calls.
"""

import json
from jira_quize import jira_refinement_copilot_v2, extract_context, detect_response_style


# ==========================================
# Mock LLM Functions (replace with real LLMs)
# ==========================================

def mock_llm_classifier(prompt: str) -> str:
    """
    Mock intent classifier.
    In production, this would call a real LLM (e.g., GPT-4, Claude, etc.)
    """
    # Simple keyword-based classification for demo purposes
    question = prompt.lower()
    
    if "acceptance" in question or "criteria" in question or "ac" in question:
        intent = "ACCEPTANCE_CRITERIA"
        confidence = 0.85
    elif "objective" in question or "purpose" in question or "why" in question:
        intent = "OBJECTIVE_INTENT"
        confidence = 0.9
    elif "figma" in question or "design" in question:
        intent = "FIGMA_ALIGNMENT"
        confidence = 0.8
    elif "scope" in question:
        intent = "SCOPE_DEFINITION"
        confidence = 0.85
    elif "edge case" in question or "risk" in question:
        intent = "EDGE_CASE_RISK_ANALYSIS"
        confidence = 0.75
    elif "ready" in question or "development" in question:
        intent = "DEVELOPMENT_READINESS"
        confidence = 0.8
    else:
        intent = "STORY_REFINEMENT"
        confidence = 0.6
    
    return json.dumps({
        "primary_intent": intent,
        "secondary_intents": [],
        "confidence": confidence
    })


def mock_llm_main(prompt: str) -> str:
    """
    Mock main LLM for response generation.
    In production, this would call a real LLM (e.g., GPT-4, Claude, etc.)
    """
    # Simple response based on the mode prompt
    if "GIVEN" in prompt and "WHEN" in prompt and "THEN" in prompt:
        return """Here are the acceptance criteria using Given/When/Then format:

**Scenario 1: Successful Password Reset**
- GIVEN a user is on the forgot password page
- WHEN they enter a valid registered email address and click 'Submit'
- THEN they should receive a password reset link via email
- AND see a confirmation message "Password reset link sent to your email"

**Scenario 2: Invalid Email**
- GIVEN a user is on the forgot password page
- WHEN they enter an unregistered email address and click 'Submit'
- THEN they should see an error message "Email not found in our system"
- AND no email should be sent

**Scenario 3: Empty Field**
- GIVEN a user is on the forgot password page
- WHEN they click 'Submit' without entering an email
- THEN they should see a validation error "Email is required"
- AND the submit button should remain enabled"""
    
    elif "Figma" in prompt:
        return """Figma Design Alignment Checklist:

✓ **Component Spacing**: Verify button padding matches Figma (16px horizontal, 12px vertical)
✓ **Typography**: Ensure font size (14px), weight (600), and family match design
✓ **Colors**: Validate button color (#007AFF), text color (#FFFFFF), hover state (#0051D5)
✓ **Icons**: Check if icon is present and matches Figma asset
✓ **Interaction States**:
  - Default: Blue background, white text
  - Hover: Darker blue with 0.2s transition
  - Active: Even darker blue with scale(0.98)
  - Disabled: Grey background (#CCCCCC), reduced opacity
✓ **Responsive Behavior**: Verify button width on mobile (100%) and desktop (auto)"""
    
    elif "objective" in prompt.lower():
        return """**Objective**: The forgot password submit button initiates a secure password recovery flow.

**Business Purpose**: 
- Allows users who have forgotten their credentials to regain access to their account
- Reduces support tickets related to password resets
- Improves user experience by enabling self-service recovery

**Primary Users**:
- Existing users who cannot remember their password
- Users who need to reset compromised passwords

**Problem Solved**:
- Eliminates the need for manual password reset by support staff
- Provides immediate access recovery option
- Maintains security while enabling convenience"""
    
    else:
        return """Based on the provided context, here's the refined analysis for the submit button:

**Functionality**: The button triggers form submission and validation
**Expected Behavior**: 
- Validates all required fields before submission
- Shows loading state during processing
- Displays success or error messages appropriately
**Key Considerations**:
- Ensure proper error handling
- Implement rate limiting to prevent abuse
- Add analytics tracking for user interactions"""


# ==========================================
# Example Usage Scenarios
# ==========================================

def run_examples():
    """Run example scenarios demonstrating the copilot's capabilities."""
    
    print("=" * 80)
    print("Jira Refinement Copilot V2.1 - Example Usage")
    print("=" * 80)
    print()
    
    # Example 1: Acceptance Criteria with Figma mention
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Acceptance Criteria (Context-Aware with Figma)")
    print("=" * 80)
    question1 = "What are the acceptance criteria for the submit button in the Figma design?"
    print(f"\n📝 Question: {question1}\n")
    
    # Show extracted context
    context1 = extract_context(question1)
    print(f"🔍 Extracted Context: {context1}\n")
    
    # Show detected style
    style1 = detect_response_style(question1)
    print(f"🎨 Detected Style: {style1}\n")
    
    # Generate response
    response1 = jira_refinement_copilot_v2(mock_llm_classifier, mock_llm_main, question1)
    print(f"💬 Response:\n{response1}\n")
    
    # Example 2: Objective Intent
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Objective Intent (High Confidence)")
    print("=" * 80)
    question2 = "What is the objective of the forgot password submit button?"
    print(f"\n📝 Question: {question2}\n")
    
    context2 = extract_context(question2)
    print(f"🔍 Extracted Context: {context2}\n")
    
    style2 = detect_response_style(question2)
    print(f"🎨 Detected Style: {style2}\n")
    
    response2 = jira_refinement_copilot_v2(mock_llm_classifier, mock_llm_main, question2)
    print(f"💬 Response:\n{response2}\n")
    
    # Example 3: Low Confidence - Triggers Clarifying Questions
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Low Confidence Scenario (Clarifying Questions)")
    print("=" * 80)
    question3 = "Tell me about the button"
    print(f"\n📝 Question: {question3}\n")
    
    # Create a mock classifier that returns low confidence
    def low_confidence_classifier(prompt):
        return json.dumps({
            "primary_intent": "ACCEPTANCE_CRITERIA",
            "secondary_intents": [],
            "confidence": 0.45  # Below threshold of 0.6
        })
    
    response3 = jira_refinement_copilot_v2(low_confidence_classifier, mock_llm_main, question3)
    print(f"💬 Response:\n{response3}\n")
    
    # Example 4: Edge Case Analysis
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Edge Case Analysis (Context-Aware)")
    print("=" * 80)
    question4 = "What are the edge cases and risks for the password reset flow?"
    print(f"\n📝 Question: {question4}\n")
    
    context4 = extract_context(question4)
    print(f"🔍 Extracted Context: {context4}\n")
    print(f"   Note: mentions_edge_cases={context4.get('mentions_edge_cases')}")
    print(f"   → This triggers special emphasis in the prompt!\n")
    
    response4 = jira_refinement_copilot_v2(mock_llm_classifier, mock_llm_main, question4)
    print(f"💬 Response:\n{response4}\n")
    
    # Example 5: Figma Alignment
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Figma Alignment Check")
    print("=" * 80)
    question5 = "Does the submit button match the Figma design?"
    print(f"\n📝 Question: {question5}\n")
    
    context5 = extract_context(question5)
    print(f"🔍 Extracted Context: {context5}\n")
    print(f"   Note: mentions_figma={context5.get('mentions_figma')}")
    print(f"   → This adds Figma-specific instructions to the prompt!\n")
    
    response5 = jira_refinement_copilot_v2(mock_llm_classifier, mock_llm_main, question5)
    print(f"💬 Response:\n{response5}\n")
    
    print("=" * 80)
    print("Examples completed!")
    print("=" * 80)


# ==========================================
# Interactive Demo
# ==========================================

def interactive_demo():
    """Interactive demo allowing user to ask questions."""
    
    print("\n" + "=" * 80)
    print("Jira Refinement Copilot V2.1 - Interactive Demo")
    print("=" * 80)
    print("\nType your questions about Jira stories, or 'quit' to exit.\n")
    
    while True:
        try:
            question = input("🤔 Your Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                print("⚠️  Please enter a question.\n")
                continue
            
            print()
            response = jira_refinement_copilot_v2(mock_llm_classifier, mock_llm_main, question)
            print(f"\n💬 Response:\n{response}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


# ==========================================
# Main Entry Point
# ==========================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        run_examples()
        
        print("\n💡 Tip: Run with --interactive flag for an interactive demo:")
        print("   python example_copilot_usage.py --interactive\n")
