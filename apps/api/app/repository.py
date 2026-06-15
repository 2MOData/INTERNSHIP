from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AgentModel
from .schemas import AgentCreate


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