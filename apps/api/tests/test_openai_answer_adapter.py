from uuid import uuid4

import pytest

from app.answer_generation import AnswerContextChunk
from app.openai_answer_adapter import (
    AnswerGenerationError,
    MissingAnswerGenerationApiKeyError,
    OpenAIAnswerGenerationAdapter,
)


class FakeResponse:
    output_text = "Réponse générée à partir du contexte."


class FakeResponsesResource:
    def __init__(self) -> None:
        self.received_model: str | None = None
        self.received_input: list[dict[str, str]] | None = None

    def create(
        self,
        *,
        model: str,
        input: list[dict[str, str]],
    ) -> FakeResponse:
        self.received_model = model
        self.received_input = input

        return FakeResponse()


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = FakeResponsesResource()


def test_generate_answer_calls_responses_api_with_context() -> None:
    fake_client = FakeOpenAIClient()

    adapter = OpenAIAnswerGenerationAdapter(
        api_key=None,
        model="fake-answer-model",
        client=fake_client,
    )

    source_id = uuid4()

    result = adapter.generate_answer(
        question="Quelle est la règle bagage ?",
        context_chunks=[
            AnswerContextChunk(
                source_id=source_id,
                page_number=2,
                text="Le passager peut transporter un bagage cabine.",
            )
        ],
    )

    assert result.answer == "Réponse générée à partir du contexte."

    assert fake_client.responses.received_model == "fake-answer-model"
    assert fake_client.responses.received_input is not None

    developer_message = fake_client.responses.received_input[0]
    user_message = fake_client.responses.received_input[1]

    assert developer_message["role"] == "developer"
    assert "répond uniquement à partir du contexte fourni" in developer_message["content"]

    assert user_message["role"] == "user"
    assert "Quelle est la règle bagage ?" in user_message["content"]
    assert "Le passager peut transporter un bagage cabine." in user_message["content"]
    assert str(source_id) in user_message["content"]
    assert "page=2" in user_message["content"]


def test_adapter_requires_api_key_without_injected_client() -> None:
    with pytest.raises(MissingAnswerGenerationApiKeyError):
        OpenAIAnswerGenerationAdapter(
            api_key=None,
            model="fake-answer-model",
        )


def test_generate_answer_rejects_empty_question() -> None:
    adapter = OpenAIAnswerGenerationAdapter(
        api_key=None,
        model="fake-answer-model",
        client=FakeOpenAIClient(),
    )

    with pytest.raises(AnswerGenerationError):
        adapter.generate_answer(
            question="   ",
            context_chunks=[],
        )