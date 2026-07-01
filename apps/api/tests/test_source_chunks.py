from fastapi.testclient import TestClient

from tests.test_sources import PDF_CONTENT, create_agent, create_corpus


def upload_ready_source(client: TestClient) -> dict[str, object]:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                PDF_CONTENT,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    return response.json()


def test_generate_source_chunks_from_extracted_pages(client: TestClient) -> None:
    source = upload_ready_source(client)

    response = client.post(f"/api/sources/{source['id']}/chunks")

    assert response.status_code == 201

    chunks = response.json()

    assert len(chunks) == 1
    assert chunks[0]["source_id"] == source["id"]
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["text"] == "Texte extrait du PDF de test."


def test_list_source_chunks(client: TestClient) -> None:
    source = upload_ready_source(client)

    created_response = client.post(f"/api/sources/{source['id']}/chunks")
    assert created_response.status_code == 201

    response = client.get(f"/api/sources/{source['id']}/chunks")

    assert response.status_code == 200
    assert response.json() == created_response.json()


def test_generate_source_chunks_is_idempotent(client: TestClient) -> None:
    source = upload_ready_source(client)

    first_response = client.post(f"/api/sources/{source['id']}/chunks")
    second_response = client.post(f"/api/sources/{source['id']}/chunks")

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert len(second_response.json()) == 1
    assert second_response.json()[0]["text"] == "Texte extrait du PDF de test."


def test_list_missing_source_chunks_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/sources/00000000-0000-0000-0000-000000000000/chunks"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Source introuvable."}


def test_generate_missing_source_chunks_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/sources/00000000-0000-0000-0000-000000000000/chunks"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Source introuvable."}