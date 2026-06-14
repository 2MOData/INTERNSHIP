from .schemas import AgentCreate, AgentRead


class InMemoryAgentRepository:
    def __init__(self) -> None:
        self._agents: list[AgentRead] = []

    def list(self) -> list[AgentRead]:
        return list(self._agents)

    def create(self, agent_data: AgentCreate) -> AgentRead:
        agent = AgentRead(**agent_data.model_dump())
        self._agents.append(agent)
        return agent


agent_repository = InMemoryAgentRepository()
