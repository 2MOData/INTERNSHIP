from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "agents-api",
    }


def test_agents_list_is_empty_initially(client: TestClient) -> None:
    response = client.get("/api/agents")

    assert response.status_code == 200
    assert response.json() == []


def test_create_agent_and_list_it(client: TestClient) -> None:
    payload = {
        "name": "Baggage Policy Agent",
        "description": "Répond aux questions relatives aux bagages.",
        "use_case": "Support passager concernant les bagages",
        "language": "fr",
    }

    create_response = client.post("/api/agents", json=payload)

    assert create_response.status_code == 201

    created_agent = create_response.json()
    assert created_agent["name"] == payload["name"]
    assert created_agent["description"] == payload["description"]
    assert created_agent["use_case"] == payload["use_case"]
    assert created_agent["language"] == "fr"
    assert created_agent["status"] == "draft"
    assert created_agent["id"]
    assert created_agent["created_at"]

    list_response = client.get("/api/agents")

    assert list_response.status_code == 200
    assert list_response.json() == [created_agent]


def test_create_agent_rejects_short_name(client: TestClient) -> None:
    response = client.post(
        "/api/agents",
        json={
            "name": "AI",
            "description": "",
            "use_case": "Support passager",
            "language": "fr",
        },
    )

    assert response.status_code == 422


def test_create_agent_rejects_unsupported_language(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/agents",
        json={
            "name": "Baggage Policy Agent",
            "description": "",
            "use_case": "Support passager",
            "language": "de",
        },
    )

    assert response.status_code == 422