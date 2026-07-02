from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class AnswerContextChunk:
    source_id: UUID
    page_number: int
    text: str


@dataclass(frozen=True)
class GeneratedAnswer:
    answer: str


class AnswerGenerationClient(Protocol):
    def generate_answer(
        self,
        *,
        question: str,
        context_chunks: list[AnswerContextChunk],
    ) -> GeneratedAnswer:
        pass