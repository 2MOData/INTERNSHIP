from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from .repository import agent_repository
from .schemas import AgentCreate, AgentRead

app = FastAPI(
    title="Domain-Specific Knowledge Agents API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "agents-api",
    }

@app.get("/api/agents", response_model=list[AgentRead], tags=["agents"])
def list_agents() -> list[AgentRead]:
    return agent_repository.list()


@app.post(
    "/api/agents",
    response_model=AgentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["agents"],
)
def create_agent(agent_data: AgentCreate) -> AgentRead:
    return agent_repository.create(agent_data)