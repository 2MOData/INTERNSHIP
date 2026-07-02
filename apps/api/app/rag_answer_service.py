from dataclasses import dataclass
from uuid import UUID

from .answer_generation import (
    AnswerContextChunk,
    AnswerGenerationClient,
)
from .corpus_search_service import CorpusSearchService


class NoRelevantContextError(ValueError):
    pass


@dataclass(frozen=True)
class RagAnswerSource:
    chunk_id: UUID
    source_id: UUID
    page_number: int
    text: str
    score: float


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    sources: list[RagAnswerSource]


class RagAnswerService:
    def __init__(
        self,
        *,
        corpus_search_service: CorpusSearchService,
        answer_generation_client: AnswerGenerationClient,
    ) -> None:
        self._corpus_search_service = corpus_search_service
        self._answer_generation_client = answer_generation_client

    def answer(
        self,
        *,
        corpus_id: UUID,
        question: str,
        limit: int,
    ) -> RagAnswer:
        search_results = self._corpus_search_service.search(
            corpus_id=corpus_id,
            query=question,
            limit=limit,
        )

        if not search_results:
            raise NoRelevantContextError

        context_chunks = [
            AnswerContextChunk(
                source_id=result.source_id,
                page_number=result.page_number,
                text=result.text,
            )
            for result in search_results
        ]

        generated_answer = self._answer_generation_client.generate_answer(
            question=question,
            context_chunks=context_chunks,
        )

        return RagAnswer(
            answer=generated_answer.answer,
            sources=[
                RagAnswerSource(
                    chunk_id=result.chunk_id,
                    source_id=result.source_id,
                    page_number=result.page_number,
                    text=result.text,
                    score=result.score,
                )
                for result in search_results
            ],
        )