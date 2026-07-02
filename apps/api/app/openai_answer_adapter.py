from openai import OpenAI

from .answer_generation import AnswerContextChunk, GeneratedAnswer


class AnswerGenerationError(RuntimeError):
    pass


class MissingAnswerGenerationApiKeyError(AnswerGenerationError):
    pass


class OpenAIAnswerGenerationAdapter:
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        client: object | None = None,
    ) -> None:
        if client is None and not api_key:
            raise MissingAnswerGenerationApiKeyError

        self._client = client or OpenAI(api_key=api_key)
        self._model = model

    def generate_answer(
        self,
        *,
        question: str,
        context_chunks: list[AnswerContextChunk],
    ) -> GeneratedAnswer:
        normalized_question = " ".join(question.split())

        if not normalized_question:
            raise AnswerGenerationError("La question est vide.")

        response = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "developer",
                    "content": self._build_developer_instructions(),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(
                        question=normalized_question,
                        context_chunks=context_chunks,
                    ),
                },
            ],
        )

        answer = response.output_text.strip()

        if not answer:
            raise AnswerGenerationError("Le modèle n'a pas produit de réponse.")

        return GeneratedAnswer(answer=answer)

    def _build_developer_instructions(self) -> str:
        return (
            "Tu es un assistant spécialisé qui répond uniquement à partir du "
            "contexte fourni. Si le contexte ne contient pas l'information, "
            "dis clairement que tu ne sais pas. Réponds en français. "
            "Ne fabrique pas de sources."
        )

    def _build_user_prompt(
        self,
        *,
        question: str,
        context_chunks: list[AnswerContextChunk],
    ) -> str:
        context = "\n\n".join(
            (
                f"[Source {index} | source_id={chunk.source_id} | "
                f"page={chunk.page_number}]\n{chunk.text}"
            )
            for index, chunk in enumerate(context_chunks, start=1)
        )

        return (
            "Question utilisateur :\n"
            f"{question}\n\n"
            "Contexte disponible :\n"
            f"{context}"
        )