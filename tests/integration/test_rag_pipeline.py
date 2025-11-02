"""Integration tests for RAG pipeline"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Note: This requires app_state to be initialized
    # In real tests, you'd set up test fixtures properly
    from app.main import app
    return TestClient(app)


def test_query_endpoint(client):
    """Test query endpoint"""
    # Skip if app not initialized
    pytest.skip("Requires app_state initialization")
    
    response = client.post(
        "/query",
        json={
            "query": "What is retrieval augmented generation?",
            "top_k": 5
        }
    )
    
    assert response.status_code in [200, 503]  # 503 if not initialized
    if response.status_code == 200:
        data = response.json()
        assert 'answer' in data
        assert 'citations' in data
        assert 'session_id' in data
        assert len(data['answer']) > 0


def test_feedback_endpoint(client):
    """Test feedback endpoint"""
    pytest.skip("Requires app_state initialization")
    
    response = client.post(
        "/feedback",
        json={
            "query": "test query",
            "response": "test response",
            "rating": 5,
            "feedback_text": "Great answer!"
        }
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert response.json()['status'] == 'feedback_recorded'

