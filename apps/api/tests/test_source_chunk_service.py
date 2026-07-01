import pytest


from app.source_repository import SourceRepository
from app.source_chunk_service import SourceHasNoExtractedPagesError

from tests.test_sources import create_agent, create_corpus


def test_generate_for_source_creates_chunks_from_pages(client) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    upload_response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                b"%PDF-1.4\n%%EOF\n",
                "application/pdf",
            )
        },
    )

    source = upload_response.json()

    response = client.post(f"/api/sources/{source['id']}/chunks")

    assert response.status_code == 201
    chunks = response.json()

    assert len(chunks) >= 1
    assert chunks[0]["source_id"] == source["id"]
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["chunk_index"] == 0