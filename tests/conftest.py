"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app
from models import OptionAnalysis, ComparisonResponse


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_comparison_request():
    """Sample comparison request for testing."""
    return {
        "question": "Which API should I use for my e-commerce project?",
        "options": ["Stripe API", "PayPal API", "Square API"],
        "criteria": ["Integration complexity", "Fees", "Feature set", "Documentation"],
        "context": "Small startup with limited development resources"
    }


@pytest.fixture
def sample_comparison_response():
    """Sample comparison response for testing."""
    return ComparisonResponse(
        question="Which API should I use for my e-commerce project?",
        analysis={
            "Stripe API": OptionAnalysis(
                strengths=[
                    "Excellent documentation and developer experience",
                    "Comprehensive feature set including subscriptions",
                    "Strong fraud protection"
                ],
                weaknesses=[
                    "Higher transaction fees for small volumes",
                    "Complex pricing structure"
                ],
                explanation="Stripe offers the most developer-friendly experience with excellent documentation and comprehensive features. However, the pricing can be complex and fees may be higher for smaller transaction volumes."
            ),
            "PayPal API": OptionAnalysis(
                strengths=[
                    "Widely recognized brand increases customer trust",
                    "Lower fees for certain transaction types",
                    "Built-in buyer protection"
                ],
                weaknesses=[
                    "More complex integration process",
                    "Limited customization options",
                    "Potential account holds and restrictions"
                ],
                explanation="PayPal provides strong brand recognition and customer trust, which can improve conversion rates. However, integration is more complex and there are potential issues with account restrictions."
            )
        },
        trade_offs="For a small startup with limited development resources, Stripe offers the fastest path to implementation despite higher fees. PayPal provides better brand recognition but requires more development effort.",
        context_notes="Given your startup context, prioritize development speed over marginal fee savings. Stripe's superior documentation will save significant development time."
    )


@pytest.fixture
def mock_llm_analyzer():
    """Mock LLM analyzer for testing without API calls."""
    with patch('main.analyzer') as mock_analyzer:
        def mock_analyze_options(question, options, criteria, context=None):
            return ComparisonResponse(
                question=question,  # Return the actual question passed in
                analysis={
                    option: OptionAnalysis(
                        strengths=[f"Strength 1 for {option}", f"Strength 2 for {option}"],
                        weaknesses=[f"Weakness 1 for {option}"],
                        explanation=f"Test explanation for {option}"
                    ) for option in options
                },
                trade_offs="Test trade-offs analysis",
                context_notes="Test context notes" if context else None
            )
        
        mock_analyzer.analyze_options.side_effect = mock_analyze_options
        yield mock_analyzer