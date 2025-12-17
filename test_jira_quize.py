#!/usr/bin/env python3
"""
Unit tests for Jira Refinement Copilot V2.1

Tests key modular components:
- extract_context
- detect_response_style
- classify_intent
- assumption_gate
- compose_final_prompt
"""

import json
import unittest
from unittest.mock import Mock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jira_quize import (
    extract_context,
    detect_response_style,
    classify_intent,
    assumption_gate,
    compose_final_prompt,
    MASTER_PROMPT,
    MODE_PROMPTS,
    INTENT_THRESHOLDS,
    CLARIFYING_QUESTIONS
)


class TestExtractContext(unittest.TestCase):
    """Test context extraction from user questions."""
    
    def test_ui_related_detection(self):
        """Test detection of UI-related questions."""
        question = "What happens when I click the submit button?"
        context = extract_context(question)
        self.assertTrue(context["ui_related"])
        self.assertIn("mentions_figma", context)
    
    def test_figma_mention_detection(self):
        """Test detection of Figma mentions."""
        question = "Does this match the Figma design?"
        context = extract_context(question)
        self.assertTrue(context["mentions_figma"])
    
    def test_scope_detection(self):
        """Test detection of scope-related questions."""
        question = "What is in scope for this feature?"
        context = extract_context(question)
        self.assertTrue(context["mentions_scope"])
    
    def test_acceptance_criteria_detection(self):
        """Test detection of AC-related questions."""
        question = "What are the acceptance criteria?"
        context = extract_context(question)
        self.assertTrue(context["mentions_ac"])
    
    def test_readiness_detection(self):
        """Test detection of readiness questions."""
        question = "Is this ready for development?"
        context = extract_context(question)
        self.assertTrue(context["mentions_ready"])
    
    def test_edge_case_detection(self):
        """Test detection of edge case questions."""
        question = "What are the edge cases and risks?"
        context = extract_context(question)
        self.assertTrue(context["mentions_edge_cases"])
    
    def test_business_rules_detection(self):
        """Test detection of business rule questions."""
        question = "What validation rules apply here?"
        context = extract_context(question)
        self.assertTrue(context["mentions_business_rules"])
    
    def test_multiple_contexts(self):
        """Test extraction of multiple context flags."""
        question = "What are the acceptance criteria for the Figma button design?"
        context = extract_context(question)
        self.assertTrue(context["ui_related"])
        self.assertTrue(context["mentions_figma"])
        self.assertTrue(context["mentions_ac"])


class TestDetectResponseStyle(unittest.TestCase):
    """Test response style detection."""
    
    def test_conversational_style(self):
        """Test detection of conversational questions."""
        questions = [
            "Just explain what this feature does",
            "In simple terms, what is the objective?",
            "Why do we need this?"
        ]
        for question in questions:
            style = detect_response_style(question)
            self.assertEqual(style, "CONVERSATIONAL", f"Failed for: {question}")
    
    def test_structured_style(self):
        """Test detection of structured questions."""
        questions = [
            "List the acceptance criteria",
            "Define the scope",
            "What are the criteria for readiness?"
        ]
        for question in questions:
            style = detect_response_style(question)
            self.assertEqual(style, "STRUCTURED", f"Failed for: {question}")
    
    def test_hybrid_style(self):
        """Test detection of hybrid questions."""
        question = "Tell me about the submit button"
        style = detect_response_style(question)
        self.assertEqual(style, "HYBRID")


class TestClassifyIntent(unittest.TestCase):
    """Test intent classification."""
    
    def test_successful_classification(self):
        """Test successful intent classification with valid JSON."""
        mock_llm = Mock(return_value=json.dumps({
            "primary_intent": "OBJECTIVE_INTENT",
            "secondary_intents": ["SCOPE_DEFINITION"],
            "confidence": 0.85
        }))
        
        result = classify_intent(mock_llm, "What is the objective?")
        
        self.assertEqual(result["primary"], "OBJECTIVE_INTENT")
        self.assertEqual(result["secondary"], ["SCOPE_DEFINITION"])
        self.assertEqual(result["confidence"], 0.85)
    
    def test_classification_with_invalid_json(self):
        """Test graceful fallback with invalid JSON."""
        mock_llm = Mock(return_value="Not valid JSON")
        
        result = classify_intent(mock_llm, "What is the objective?")
        
        self.assertEqual(result["primary"], "STORY_REFINEMENT")
        self.assertEqual(result["secondary"], [])
        self.assertLess(result["confidence"], 0.5)
    
    def test_classification_with_missing_fields(self):
        """Test handling of partial JSON response."""
        mock_llm = Mock(return_value=json.dumps({
            "primary_intent": "ACCEPTANCE_CRITERIA"
        }))
        
        result = classify_intent(mock_llm, "What are the AC?")
        
        self.assertEqual(result["primary"], "ACCEPTANCE_CRITERIA")
        self.assertEqual(result["secondary"], [])
        self.assertIsInstance(result["confidence"], (int, float))
    
    def test_classification_with_exception(self):
        """Test handling of LLM exceptions."""
        mock_llm = Mock(side_effect=Exception("LLM error"))
        
        result = classify_intent(mock_llm, "What is the objective?")
        
        self.assertEqual(result["primary"], "STORY_REFINEMENT")
        self.assertLess(result["confidence"], 0.5)


class TestAssumptionGate(unittest.TestCase):
    """Test assumption gate logic."""
    
    def test_assumptions_needed_for_ac_without_ui(self):
        """Test that AC without UI context needs assumptions."""
        context = {"ui_related": False}
        needs_assumptions = assumption_gate("ACCEPTANCE_CRITERIA", context)
        self.assertTrue(needs_assumptions)
    
    def test_no_assumptions_for_ac_with_ui(self):
        """Test that AC with UI context doesn't need assumptions."""
        context = {"ui_related": True}
        needs_assumptions = assumption_gate("ACCEPTANCE_CRITERIA", context)
        self.assertFalse(needs_assumptions)
    
    def test_assumptions_for_figma_without_mention(self):
        """Test that Figma alignment without mention needs assumptions."""
        context = {"mentions_figma": False}
        needs_assumptions = assumption_gate("FIGMA_ALIGNMENT", context)
        self.assertTrue(needs_assumptions)
    
    def test_no_assumptions_for_figma_with_mention(self):
        """Test that Figma alignment with mention doesn't need assumptions."""
        context = {"mentions_figma": True}
        needs_assumptions = assumption_gate("FIGMA_ALIGNMENT", context)
        self.assertFalse(needs_assumptions)
    
    def test_assumptions_for_scope_without_mention(self):
        """Test that scope without mention needs assumptions."""
        context = {"mentions_scope": False}
        needs_assumptions = assumption_gate("SCOPE_DEFINITION", context)
        self.assertTrue(needs_assumptions)
    
    def test_no_assumptions_for_other_intents(self):
        """Test that other intents don't trigger assumptions by default."""
        context = {}
        needs_assumptions = assumption_gate("OBJECTIVE_INTENT", context)
        self.assertFalse(needs_assumptions)


class TestComposeFinalPrompt(unittest.TestCase):
    """Test final prompt composition."""
    
    def test_basic_prompt_composition(self):
        """Test basic prompt composition."""
        prompt = compose_final_prompt(
            master=MASTER_PROMPT,
            mode_prompt=MODE_PROMPTS["OBJECTIVE_INTENT"],
            question="What is the objective?",
            context={"ui_related": False},
            style="CONVERSATIONAL",
            require_assumptions=False
        )
        
        self.assertIn(MASTER_PROMPT, prompt)
        self.assertIn("CONVERSATIONAL", prompt)
        self.assertIn("What is the objective?", prompt)
    
    def test_prompt_with_assumptions(self):
        """Test prompt composition with assumptions enabled."""
        prompt = compose_final_prompt(
            master=MASTER_PROMPT,
            mode_prompt=MODE_PROMPTS["ACCEPTANCE_CRITERIA"],
            question="What are the AC?",
            context={"ui_related": False},
            style="STRUCTURED",
            require_assumptions=True
        )
        
        self.assertIn("assumptions", prompt.lower())
        self.assertIn("clarification", prompt.lower())
    
    def test_prompt_with_figma_context(self):
        """Test prompt includes Figma emphasis when mentioned."""
        prompt = compose_final_prompt(
            master=MASTER_PROMPT,
            mode_prompt=MODE_PROMPTS["UI_UX_BEHAVIOUR"],
            question="Check the Figma design",
            context={"mentions_figma": True, "ui_related": True},
            style="STRUCTURED",
            require_assumptions=False
        )
        
        self.assertIn("Figma", prompt)
        self.assertIn("design alignment", prompt.lower())
    
    def test_prompt_with_edge_case_context(self):
        """Test prompt emphasizes edge cases when mentioned."""
        prompt = compose_final_prompt(
            master=MASTER_PROMPT,
            mode_prompt=MODE_PROMPTS["EDGE_CASE_RISK_ANALYSIS"],
            question="What are the edge cases?",
            context={"mentions_edge_cases": True},
            style="STRUCTURED",
            require_assumptions=False
        )
        
        self.assertIn("edge case", prompt.lower())


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow."""
    
    def test_configuration_completeness(self):
        """Test that all intents have corresponding configurations."""
        # All intents from MODE_PROMPTS should have thresholds
        for intent in MODE_PROMPTS.keys():
            self.assertIn(intent, INTENT_THRESHOLDS, f"Missing threshold for {intent}")
            self.assertIn(intent, CLARIFYING_QUESTIONS, f"Missing clarifying question for {intent}")
    
    def test_threshold_values_are_valid(self):
        """Test that all threshold values are between 0 and 1."""
        for intent, threshold in INTENT_THRESHOLDS.items():
            self.assertGreaterEqual(threshold, 0.0, f"Invalid threshold for {intent}")
            self.assertLessEqual(threshold, 1.0, f"Invalid threshold for {intent}")
    
    def test_mode_prompts_have_enhanced_content(self):
        """Test that MODE_PROMPTS contain enhanced templates/examples."""
        # Check that acceptance criteria has the Given/When/Then template
        ac_prompt = MODE_PROMPTS["ACCEPTANCE_CRITERIA"]
        self.assertIn("GIVEN", ac_prompt)
        self.assertIn("WHEN", ac_prompt)
        self.assertIn("THEN", ac_prompt)


def run_tests():
    """Run all tests with detailed output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
