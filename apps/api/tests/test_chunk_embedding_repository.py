from app.chunk_embedding_repository import ChunkEmbeddingRepository
from app.models import AgentModel, CorpusModel, SourceChunkModel, SourceModel


def create_persisted_chunk(test_session) -> SourceChunkModel:
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

    return chunk


def test_upsert_for_chunk_creates_embedding(test_session) -> None:
    chunk = create_persisted_chunk(test_session)
    repository = ChunkEmbeddingRepository(test_session)

    embedding = repository.upsert_for_chunk(
        chunk_id=chunk.id,
        embedding_model="test-embedding-model",
        embedding=[0.1] * 1536,
    )

    assert embedding.chunk_id == chunk.id
    assert embedding.embedding_model == "test-embedding-model"
    assert embedding.embedding_dimensions == 1536
    assert list(embedding.embedding) == [0.1] * 1536


def test_upsert_for_chunk_replaces_existing_embedding(test_session) -> None:
    chunk = create_persisted_chunk(test_session)
    repository = ChunkEmbeddingRepository(test_session)

    first_embedding = repository.upsert_for_chunk(
        chunk_id=chunk.id,
        embedding_model="first-model",
        embedding=[0.1] * 1536,
    )

    second_embedding = repository.upsert_for_chunk(
        chunk_id=chunk.id,
        embedding_model="second-model",
        embedding=[0.2] * 1536,
    )

    assert second_embedding.id == first_embedding.id
    assert second_embedding.embedding_model == "second-model"
    assert second_embedding.embedding_dimensions == 1536
    assert list(second_embedding.embedding) == [0.2] * 1536


def test_get_for_chunk_returns_embedding(test_session) -> None:
    chunk = create_persisted_chunk(test_session)
    repository = ChunkEmbeddingRepository(test_session)

    created_embedding = repository.upsert_for_chunk(
        chunk_id=chunk.id,
        embedding_model="test-embedding-model",
        embedding=[0.1] * 1536,
    )

    found_embedding = repository.get_for_chunk(chunk.id)

    assert found_embedding is not None
    assert found_embedding.id == created_embedding.id