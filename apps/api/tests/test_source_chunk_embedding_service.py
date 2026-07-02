from app.chunk_embedding_repository import ChunkEmbeddingRepository
from app.models import AgentModel, CorpusModel, SourceChunkModel, SourceModel
from app.source_chunk_embedding_service import SourceChunkEmbeddingService
from app.source_repository import SourceRepository


class FakeEmbeddingClient:
    model = "fake-embedding-model"

    def embed_text(self, text: str) -> list[float]:
        return [0.1] * 1536


def create_source_with_chunks(test_session) -> SourceModel:
    agent = AgentModel(
        name="Agent embeddings",
        use_case="Tester les embeddings",
    )
    test_session.add(agent)
    test_session.commit()
    test_session.refresh(agent)

    corpus = CorpusModel(
        agent_id=agent.id,
        name="Corpus embeddings",
    )
    test_session.add(corpus)
    test_session.commit()
    test_session.refresh(corpus)

    source = SourceModel(
        corpus_id=corpus.id,
        source_type="pdf",
        original_filename="policy.pdf",
        content_type="application/pdf",
        size_bytes=123,
        storage_key="test/policy.pdf",
        status="ready",
    )
    test_session.add(source)
    test_session.commit()
    test_session.refresh(source)

    chunk = SourceChunkModel(
        source_id=source.id,
        page_number=1,
        chunk_index=0,
        text="Texte du chunk à vectoriser.",
    )
    test_session.add(chunk)
    test_session.commit()
    test_session.refresh(chunk)

    return source


def test_generate_for_source_creates_embeddings_for_chunks(test_session) -> None:
    source = create_source_with_chunks(test_session)

    service = SourceChunkEmbeddingService(
        source_repository=SourceRepository(test_session),
        embedding_repository=ChunkEmbeddingRepository(test_session),
        embedding_client=FakeEmbeddingClient(),
    )

    embeddings = service.generate_for_source(source.id)

    assert len(embeddings) == 1
    assert embeddings[0].embedding_model == "fake-embedding-model"
    assert embeddings[0].embedding_dimensions == 1536
    assert list(embeddings[0].embedding) == [0.1] * 1536