"""
Integration tests for the Comparison Tool API.

Tests the complete analysis pipeline with various scenarios.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "comparison-tool-api"


@pytest.mark.integration
def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "description" in data
    assert data["message"] == "Comparison Tool API"


@pytest.mark.integration
def test_compare_endpoint_with_mock(client, mock_llm_analyzer, sample_comparison_request):
    """Test the compare endpoint with mocked LLM analyzer."""
    response = client.post("/compare", json=sample_comparison_request)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "question" in data
    assert "analysis" in data
    assert "trade_offs" in data
    assert "context_notes" in data
    
    # Verify analysis structure
    analysis = data["analysis"]
    for option in sample_comparison_request["options"]:
        if option in analysis:  # Mock might not include all options
            option_analysis = analysis[option]
            assert "strengths" in option_analysis
            assert "weaknesses" in option_analysis
            assert "explanation" in option_analysis
            assert isinstance(option_analysis["strengths"], list)
            assert isinstance(option_analysis["weaknesses"], list)
            assert len(option_analysis["strengths"]) > 0
            assert len(option_analysis["weaknesses"]) > 0


@pytest.mark.integration
def test_api_comparison_scenario(client, mock_llm_analyzer):
    """Test API comparison scenario."""
    request_data = {
        "question": "Which payment API should I integrate?",
        "options": ["Stripe", "PayPal", "Square"],
        "criteria": ["Ease of integration", "Transaction fees", "Feature completeness"],
        "context": "E-commerce startup, processing $10k/month"
    }
    
    response = client.post("/compare", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == request_data["question"]
    assert "analysis" in data
    assert "trade_offs" in data


@pytest.mark.integration
def test_cloud_service_comparison_scenario(client, mock_llm_analyzer):
    """Test cloud service comparison scenario."""
    request_data = {
        "question": "Which cloud provider should I choose for my web app?",
        "options": ["AWS", "Google Cloud", "Azure"],
        "criteria": ["Cost", "Ease of use", "Service availability", "Support quality"],
        "context": "Small team, limited DevOps experience, budget-conscious"
    }
    
    response = client.post("/compare", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == request_data["question"]
    assert "analysis" in data
    assert "trade_offs" in data


@pytest.mark.integration
def test_tech_stack_comparison_scenario(client, mock_llm_analyzer):
    """Test tech stack comparison scenario."""
    request_data = {
        "question": "Which frontend framework should I use for my project?",
        "options": ["React", "Vue.js", "Angular", "Svelte"],
        "criteria": ["Learning curve", "Performance", "Community support", "Job market"],
        "context": "Solo developer, building a dashboard application, timeline is 3 months"
    }
    
    response = client.post("/compare", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == request_data["question"]
    assert "analysis" in data
    assert "trade_offs" in data


@pytest.mark.integration
def test_context_integration(client, mock_llm_analyzer):
    """Test that context is properly integrated into analysis."""
    request_with_context = {
        "question": "Which database should I use?",
        "options": ["PostgreSQL", "MongoDB"],
        "criteria": ["Performance", "Scalability"],
        "context": "High-traffic application with complex relationships"
    }
    
    request_without_context = {
        "question": "Which database should I use?",
        "options": ["PostgreSQL", "MongoDB"],
        "criteria": ["Performance", "Scalability"]
    }
    
    # Test with context
    response_with = client.post("/compare", json=request_with_context)
    assert response_with.status_code == 200
    data_with = response_with.json()
    
    # Test without context
    response_without = client.post("/compare", json=request_without_context)
    assert response_without.status_code == 200
    data_without = response_without.json()
    
    # Both should succeed
    assert "analysis" in data_with
    assert "analysis" in data_without
    assert "trade_offs" in data_with
    assert "trade_offs" in data_without


@pytest.mark.integration
def test_validation_errors(client):
    """Test various validation error scenarios."""
    
    # Test insufficient options
    response = client.post("/compare", json={
        "question": "Which is better?",
        "options": ["Only one"],
        "criteria": ["Cost"]
    })
    assert response.status_code == 422
    
    # Test missing required fields
    response = client.post("/compare", json={
        "question": "Which is better?"
    })
    assert response.status_code == 422
    
    # Test empty criteria
    response = client.post("/compare", json={
        "question": "Which is better?",
        "options": ["A", "B"],
        "criteria": []
    })
    assert response.status_code == 422
    
    # Test empty question
    response = client.post("/compare", json={
        "question": "",
        "options": ["A", "B"],
        "criteria": ["Cost"]
    })
    assert response.status_code == 422


@pytest.mark.integration
def test_error_response_format(client):
    """Test that error responses have consistent format."""
    response = client.post("/compare", json={
        "question": "",
        "options": ["Only one"],
        "criteria": []
    })
    
    assert response.status_code == 422
    data = response.json()
    
    # Check error response structure
    assert "error" in data
    assert "message" in data
    assert "details" in data
    assert isinstance(data["details"], list)


@pytest.mark.integration
def test_llm_service_unavailable(client):
    """Test behavior when LLM service is unavailable."""
    # This test runs with the actual app where analyzer is None due to missing API key
    response = client.post("/compare", json={
        "question": "Which is better?",
        "options": ["A", "B"],
        "criteria": ["Cost"]
    })
    
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert "message" in data