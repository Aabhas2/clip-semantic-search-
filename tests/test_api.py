from fastapi.testclient import TestClient 
from src.main import app 

client = TestClient(app) 

def test_health(): 
    response = client.get("/health") 

    assert response.status_code == 200 
    assert response.json() == {"status": "ok"} 

def test_search_returns_results(): 
    response = client.post(
        "/search",
        json={"query": "a black handbag", "limit": 5}, 
    )

    assert response.status_code == 200 

    data = response.json() 

    assert data["query"] == "a black handbag" 
    assert len(data["results"]) == 5 

    scores = [result["score"] for result in data["results"]] 

    assert scores == sorted(scores, reverse=True) 

    for result in data["results"]: 
        assert "image_url" in result 
        assert result["image_url"].startswith(
            "http://127.0.0.1:8000/images/"
        )

def test_empty_query_is_rejected(): 
    response = client.post(
        "/search", 
        json={"query": "", "limit": 5}, 
    )

    assert response.status_code == 422