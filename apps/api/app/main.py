from fastapi import Depends, FastAPI, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_database_session
from fastapi.middleware.cors import CORSMiddleware

from .repository import AgentRepository
from .schemas import AgentCreate, AgentRead

app = FastAPI(
    title="Domain-Specific Knowledge Agents API",
    version="0.1.0",
)
def get_agent_repository(
    session: Session = Depends(get_database_session),
) -> AgentRepository:
    return AgentRepository(session)

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

@app.get("/database/health", tags=["system"])
def database_health(
    session: Session = Depends(get_database_session),
) -> dict[str, str]:
    session.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "service": "postgresql",
    }

@app.get("/api/agents", response_model=list[AgentRead], tags=["agents"])
def list_agents(
    repository: AgentRepository = Depends(get_agent_repository),
) -> list[AgentRead]:
    return repository.list()


@app.post(
    "/api/agents",
    response_model=AgentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["agents"],
)
def create_agent(
    agent_data: AgentCreate,
    repository: AgentRepository = Depends(get_agent_repository),
) -> AgentRead:
    return repository.create(agent_data)