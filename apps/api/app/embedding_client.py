from openai import OpenAI


class EmbeddingProviderError(RuntimeError):
    pass


class MissingEmbeddingApiKeyError(EmbeddingProviderError):
    pass


class OpenAIEmbeddingClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        dimensions: int,
    ) -> None:
        if not api_key:
            raise MissingEmbeddingApiKeyError

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._dimensions = dimensions

    @property
    def model(self) -> str:
        return self._model

    def embed_text(self, text: str) -> list[float]:
        normalized_text = " ".join(text.split())

        if not normalized_text:
            raise EmbeddingProviderError("Le texte à vectoriser est vide.")

        response = self._client.embeddings.create(
            model=self._model,
            input=normalized_text,
            dimensions=self._dimensions,
            encoding_format="float",
        )

        embedding = response.data[0].embedding

        return list(embedding)