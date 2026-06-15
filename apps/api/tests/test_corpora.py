from fastapi.testclient import TestClient


def create_agent(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/agents",
        json={
            "name": "Baggage Policy Agent",
            "description": "Répond aux questions bagages.",
            "use_case": "Support passager concernant les bagages",
            "language": "fr",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_agent_corpora_list_is_empty_initially(
    client: TestClient,
) -> None:
    agent = create_agent(client)

    response = client.get(f"/api/agents/{agent['id']}/corpora")

    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_corpus(client: TestClient) -> None:
    agent = create_agent(client)

    create_response = client.post(
        f"/api/agents/{agent['id']}/corpora",
        json={
            "name": "Politiques bagages",
            "description": "Documents publics relatifs aux bagages.",
        },
    )

    assert create_response.status_code == 201

    corpus = create_response.json()
    assert corpus["agent_id"] == agent["id"]
    assert corpus["name"] == "Politiques bagages"
    assert corpus["status"] == "empty"

    get_response = client.get(f"/api/corpora/{corpus['id']}")

    assert get_response.status_code == 200
    assert get_response.json() == corpus


def test_list_agent_corpora(client: TestClient) -> None:
    agent = create_agent(client)

    create_response = client.post(
        f"/api/agents/{agent['id']}/corpora",
        json={"name": "Politiques bagages"},
    )

    corpus = create_response.json()

    response = client.get(f"/api/agents/{agent['id']}/corpora")

    assert response.status_code == 200
    assert response.json() == [corpus]


def test_create_corpus_for_missing_agent_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/agents/00000000-0000-0000-0000-000000000000/corpora",
        json={"name": "Politiques bagages"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Agent introuvable."}


def test_get_missing_corpus_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/corpora/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Corpus introuvable."}