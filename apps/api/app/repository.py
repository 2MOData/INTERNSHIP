from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from .models import AgentModel
from .schemas import AgentCreate, AgentUpdate



class AgentNotFoundError(LookupError):
    def __init__(self, agent_id: UUID) -> None:
        super().__init__(f"Agent {agent_id} not found")
        self.agent_id = agent_id


class AgentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[AgentModel]:
        statement = select(AgentModel).order_by(AgentModel.created_at.desc())

        return list(self._session.scalars(statement))

    def create(self, agent_data: AgentCreate) -> AgentModel:
        agent = AgentModel(**agent_data.model_dump())

        self._session.add(agent)
        self._session.commit()
        self._session.refresh(agent)

        return agent

    def get(self, agent_id: UUID) -> AgentModel:
        agent = self._session.get(AgentModel, agent_id)

        if agent is None:
            raise AgentNotFoundError(agent_id)

        return agent

    def update(
        self,
        agent_id: UUID,
        agent_data: AgentUpdate,
    ) -> AgentModel:
        agent = self.get(agent_id)

        for field, value in agent_data.model_dump(exclude_unset=True).items():
            setattr(agent, field, value)

        self._session.commit()
        self._session.refresh(agent)

        return agent

    def publish(self, agent_id: UUID) -> AgentModel:
        agent = self.get(agent_id)
        agent.status = "published"

        self._session.commit()
        self._session.refresh(agent)

        return agent