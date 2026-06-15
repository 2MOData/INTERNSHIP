from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from uuid import UUID

from .database import get_database_session
from fastapi.middleware.cors import CORSMiddleware

from .repository import AgentNotFoundError, AgentRepository
from .schemas import AgentCreate, AgentRead, AgentUpdate
from .corpus_repository import (
    AgentNotFoundForCorpusError,
    CorpusNotFoundError,
    CorpusRepository,
)
from .schemas import CorpusCreate, CorpusRead

app = FastAPI(
    title="Domain-Specific Knowledge Agents API",
    version="0.1.0",
)

def get_agent_repository(
    session: Session = Depends(get_database_session),
) -> AgentRepository:
    return AgentRepository(session)

def agent_not_found_http_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Agent introuvable.",
    )

def get_corpus_repository(
    session: Session = Depends(get_database_session),
) -> CorpusRepository:
    return CorpusRepository(session)

def corpus_not_found_http_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Corpus introuvable.",
    )


def agent_not_found_for_corpus_http_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Agent introuvable.",
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

@app.get(
    "/api/agents/{agent_id}",
    response_model=AgentRead,
    tags=["agents"],
)
def get_agent(
    agent_id: UUID,
    repository: AgentRepository = Depends(get_agent_repository),
) -> AgentRead:
    try:
        return repository.get(agent_id)
    except AgentNotFoundError as error:
        raise agent_not_found_http_exception() from error

@app.get(
    "/api/agents/{agent_id}/corpora",
    response_model=list[CorpusRead],
    tags=["corpora"],
)
def list_agent_corpora(
    agent_id: UUID,
    repository: CorpusRepository = Depends(get_corpus_repository),
) -> list[CorpusRead]:
    try:
        return repository.list_for_agent(agent_id)
    except AgentNotFoundForCorpusError as error:
        raise agent_not_found_for_corpus_http_exception() from error

@app.get(
    "/api/corpora/{corpus_id}",
    response_model=CorpusRead,
    tags=["corpora"],
)
def get_corpus(
    corpus_id: UUID,
    repository: CorpusRepository = Depends(get_corpus_repository),
) -> CorpusRead:
    try:
        return repository.get(corpus_id)
    except CorpusNotFoundError as error:
        raise corpus_not_found_http_exception() from error

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

@app.post(
    "/api/agents/{agent_id}/publish",
    response_model=AgentRead,
    tags=["agents"],
)
def publish_agent(
    agent_id: UUID,
    repository: AgentRepository = Depends(get_agent_repository),
) -> AgentRead:
    try:
        return repository.publish(agent_id)
    except AgentNotFoundError as error:
        raise agent_not_found_http_exception() from error

@app.post(
    "/api/agents/{agent_id}/corpora",
    response_model=CorpusRead,
    status_code=status.HTTP_201_CREATED,
    tags=["corpora"],
)
def create_agent_corpus(
    agent_id: UUID,
    corpus_data: CorpusCreate,
    repository: CorpusRepository = Depends(get_corpus_repository),
) -> CorpusRead:
    try:
        return repository.create_for_agent(agent_id, corpus_data)
    except AgentNotFoundForCorpusError as error:
        raise agent_not_found_for_corpus_http_exception() from error

@app.patch(
    "/api/agents/{agent_id}",
    response_model=AgentRead,
    tags=["agents"],
)
def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    repository: AgentRepository = Depends(get_agent_repository),
) -> AgentRead:
    try:
        return repository.update(agent_id, agent_data)
    except AgentNotFoundError as error:
        raise agent_not_found_http_exception() from error

