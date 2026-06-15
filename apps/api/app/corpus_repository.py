from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AgentModel, CorpusModel
from .schemas import CorpusCreate


class CorpusNotFoundError(LookupError):
    def __init__(self, corpus_id: UUID) -> None:
        super().__init__(f"Corpus {corpus_id} not found")
        self.corpus_id = corpus_id


class AgentNotFoundForCorpusError(LookupError):
    def __init__(self, agent_id: UUID) -> None:
        super().__init__(f"Agent {agent_id} not found")
        self.agent_id = agent_id


class CorpusRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_agent(self, agent_id: UUID) -> list[CorpusModel]:
        self._ensure_agent_exists(agent_id)

        statement = (
            select(CorpusModel)
            .where(CorpusModel.agent_id == agent_id)
            .order_by(CorpusModel.created_at.desc())
        )

        return list(self._session.scalars(statement))

    def create_for_agent(
        self,
        agent_id: UUID,
        corpus_data: CorpusCreate,
    ) -> CorpusModel:
        self._ensure_agent_exists(agent_id)

        corpus = CorpusModel(
            agent_id=agent_id,
            **corpus_data.model_dump(),
        )

        self._session.add(corpus)
        self._session.commit()
        self._session.refresh(corpus)

        return corpus

    def get(self, corpus_id: UUID) -> CorpusModel:
        corpus = self._session.get(CorpusModel, corpus_id)

        if corpus is None:
            raise CorpusNotFoundError(corpus_id)

        return corpus

    def _ensure_agent_exists(self, agent_id: UUID) -> None:
        if self._session.get(AgentModel, agent_id) is None:
            raise AgentNotFoundForCorpusError(agent_id)