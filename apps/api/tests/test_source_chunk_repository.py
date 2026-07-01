from uuid import UUID

from app.models import SourcePageModel
from app.source_repository import SourceRepository
from app.text_chunker import TextChunk

from tests.test_sources import create_agent, create_corpus


def test_replace_chunks_persists_chunks_in_order(client, test_session) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    source_response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                b"%PDF-1.4\n%%EOF\n",
                "application/pdf",
            )
        },
    )
    source = source_response.json()

    repository = SourceRepository(test_session)

    chunks = repository.replace_chunks(
        source_id=UUID(source["id"]),
        chunks=[
            TextChunk(page_number=1, chunk_index=0, text="Premier chunk"),
            TextChunk(page_number=1, chunk_index=1, text="Deuxième chunk"),
        ],
    )

    assert len(chunks) == 2

    listed_chunks = repository.list_chunks(UUID(source["id"]))
    assert [chunk.text for chunk in listed_chunks] == [
        "Premier chunk",
        "Deuxième chunk",
    ]