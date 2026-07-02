from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app, get_rag_answer_service
from app.rag_answer_service import NoRelevantContextError, RagAnswer, RagAnswerSource
from tests.test_sources import create_agent, create_corpus


class FakeRagAnswerService:
    def __init__(self) -> None:
        self.received_corpus_id: UUID | None = None
        self.received_question: str | None = None
        self.received_limit: int | None = None

    def answer(
        self,
        *,
        corpus_id: UUID,
        question: str,
        limit: int,
    ) -> RagAnswer:
        self.received_corpus_id = corpus_id
        self.received_question = question
        self.received_limit = limit

        return RagAnswer(
            answer="Réponse finale sourcée.",
            sources=[
                RagAnswerSource(
                    chunk_id=uuid4(),
                    source_id=uuid4(),
                    page_number=4,
                    text="Source utilisée.",
                    score=0.21,
                )
            ],
        )


class FakeNoContextRagAnswerService:
    def answer(
        self,
        *,
        corpus_id: UUID,
        question: str,
        limit: int,
    ) -> RagAnswer:
        raise NoRelevantContextError


def test_answer_corpus_question_returns_answer_and_sources(
    client: TestClient,
) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    fake_service = FakeRagAnswerService()

    def override_rag_answer_service() -> FakeRagAnswerService:
        return fake_service

    app.dependency_overrides[get_rag_answer_service] = override_rag_answer_service

    try:
        response = client.post(
            f"/api/corpora/{corpus['id']}/answer",
            json={
                "question": "Quelle est la règle ?",
                "limit": 5,
            },
        )
    finally:
        app.dependency_overrides.pop(get_rag_answer_service, None)

    assert response.status_code == 200

    payload = response.json()

    assert payload["answer"] == "Réponse finale sourcée."
    assert len(payload["sources"]) == 1
    assert payload["sources"][0]["page_number"] == 4
    assert payload["sources"][0]["text"] == "Source utilisée."
    assert payload["sources"][0]["score"] == 0.21

    assert fake_service.received_corpus_id == UUID(corpus["id"])
    assert fake_service.received_question == "Quelle est la règle ?"
    assert fake_service.received_limit == 5


def test_answer_corpus_question_without_context_returns_404(
    client: TestClient,
) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    def override_rag_answer_service() -> FakeNoContextRagAnswerService:
        return FakeNoContextRagAnswerService()

    app.dependency_overrides[get_rag_answer_service] = override_rag_answer_service

    try:
        response = client.post(
            f"/api/corpora/{corpus['id']}/answer",
            json={
                "question": "Question sans contexte",
                "limit": 5,
            },
        )
    finally:
        app.dependency_overrides.pop(get_rag_answer_service, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Aucun contexte pertinent trouvé."}