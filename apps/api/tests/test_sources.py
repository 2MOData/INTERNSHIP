from pathlib import Path

from fastapi.testclient import TestClient

PDF_CONTENT = b"%PDF-1.4\n%%EOF\n"


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


def create_corpus(
    client: TestClient,
    agent_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/agents/{agent_id}/corpora",
        json={
            "name": "Politiques bagages",
            "description": "Documents publics relatifs aux bagages.",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_upload_pdf_source(
    client: TestClient,
    document_storage_path: Path,
) -> None:
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

    source = response.json()
    assert source["corpus_id"] == corpus["id"]
    assert source["source_type"] == "pdf"
    assert source["original_filename"] == "policy.pdf"
    assert source["content_type"] == "application/pdf"
    assert source["size_bytes"] == len(PDF_CONTENT)
    assert source["status"] == "uploaded"

    stored_files = list(document_storage_path.rglob("*.pdf"))

    assert len(stored_files) == 1
    assert stored_files[0].read_bytes() == PDF_CONTENT

def test_list_corpus_sources(client: TestClient) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    upload_response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                PDF_CONTENT,
                "application/pdf",
            )
        },
    )

    source = upload_response.json()

    response = client.get(f"/api/corpora/{corpus['id']}/sources")

    assert response.status_code == 200
    assert response.json() == [source]

def test_get_source(client: TestClient) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    upload_response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                PDF_CONTENT,
                "application/pdf",
            )
        },
    )

    source = upload_response.json()

    response = client.get(f"/api/sources/{source['id']}")

    assert response.status_code == 200
    assert response.json() == source

def test_upload_rejects_invalid_pdf(client: TestClient) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "fake.pdf",
                b"not a pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Le fichier fourni n’est pas un PDF valide."
    }

def test_upload_rejects_empty_file(client: TestClient) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "empty.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Le fichier est vide."}

def test_upload_for_missing_corpus_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/corpora/00000000-0000-0000-0000-000000000000/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                PDF_CONTENT,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Corpus introuvable."}

def test_get_missing_source_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/sources/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Source introuvable."}

def test_upload_rejects_file_above_size_limit(
    client: TestClient,
) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    oversized_pdf = b"%PDF-" + b"x" * (1024 * 1024)

    response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "large.pdf",
                oversized_pdf,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Le fichier dépasse la taille maximale autorisée."
    }