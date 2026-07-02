from uuid import uuid4

import pytest

from app.answer_generation import AnswerContextChunk, GeneratedAnswer
from app.rag_answer_service import NoRelevantContextError, RagAnswerService
from app.vector_search_repository import VectorSearchMatch


class FakeCorpusSearchService:
    def __init__(
        self,
        results: list[VectorSearchMatch],
    ) -> None:
        self._results = results
        self.received_query: str | None = None
        self.received_limit: int | None = None

    def search(
        self,
        *,
        corpus_id,
        query: str,
        limit: int,
    ) -> list[VectorSearchMatch]:
        self.received_query = query
        self.received_limit = limit

        return self._results


class FakeAnswerGenerationClient:
    def __init__(self) -> None:
        self.received_question: str | None = None
        self.received_context_chunks: list[AnswerContextChunk] | None = None

    def generate_answer(
        self,
        *,
        question: str,
        context_chunks: list[AnswerContextChunk],
    ) -> GeneratedAnswer:
        self.received_question = question
        self.received_context_chunks = context_chunks

        return GeneratedAnswer(
            answer="Réponse sourcée générée.",
        )


def test_answer_generates_response_from_search_results() -> None:
    corpus_id = uuid4()
    source_id = uuid4()
    chunk_id = uuid4()

    search_result = VectorSearchMatch(
        chunk_id=chunk_id,
        source_id=source_id,
        page_number=3,
        chunk_index=0,
        text="Contexte utile.",
        score=0.18,
    )

    search_service = FakeCorpusSearchService(results=[search_result])
    answer_client = FakeAnswerGenerationClient()

    service = RagAnswerService(
        corpus_search_service=search_service,
        answer_generation_client=answer_client,
    )

    result = service.answer(
        corpus_id=corpus_id,
        question="Quelle est la règle ?",
        limit=5,
    )

    assert search_service.received_query == "Quelle est la règle ?"
    assert search_service.received_limit == 5

    assert answer_client.received_question == "Quelle est la règle ?"
    assert answer_client.received_context_chunks == [
        AnswerContextChunk(
            source_id=source_id,
            page_number=3,
            text="Contexte utile.",
        )
    ]

    assert result.answer == "Réponse sourcée générée."
    assert len(result.sources) == 1
    assert result.sources[0].chunk_id == chunk_id
    assert result.sources[0].source_id == source_id
    assert result.sources[0].page_number == 3
    assert result.sources[0].text == "Contexte utile."
    assert result.sources[0].score == 0.18


def test_answer_rejects_empty_search_results() -> None:
    service = RagAnswerService(
        corpus_search_service=FakeCorpusSearchService(results=[]),
        answer_generation_client=FakeAnswerGenerationClient(),
    )

    with pytest.raises(NoRelevantContextError):
        service.answer(
            corpus_id=uuid4(),
            question="Question sans contexte",
            limit=5,
        )