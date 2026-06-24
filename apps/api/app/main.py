from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
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

from .config import get_settings
from .document_storage import LocalDocumentStorage
from .schemas import SourcePageRead, SourceRead
from .source_repository import (
    CorpusNotFoundForSourceError,
    SourceNotFoundError,
    SourceRepository,
)
from .source_service import (
    EmptyFileError,
    FileTooLargeError,
    InvalidPdfError,
    PdfSourceService,
)

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

def get_source_repository(
    session: Session = Depends(get_database_session),
) -> SourceRepository:
    return SourceRepository(session)


def get_pdf_source_service(
    repository: SourceRepository = Depends(get_source_repository),
) -> PdfSourceService:
    settings = get_settings()

    return PdfSourceService(
        repository=repository,
        storage=LocalDocumentStorage(settings.document_storage_path),
        max_upload_size_bytes=settings.max_upload_size_bytes,
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

@app.get(
    "/api/corpora/{corpus_id}/sources",
    response_model=list[SourceRead],
    tags=["sources"],
)
def list_corpus_sources(
    corpus_id: UUID,
    repository: SourceRepository = Depends(get_source_repository),
) -> list[SourceRead]:
    try:
        return repository.list_for_corpus(corpus_id)
    except CorpusNotFoundForSourceError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corpus introuvable.",
        ) from error
        
@app.get(
    "/api/sources/{source_id}",
    response_model=SourceRead,
    tags=["sources"],
)
def get_source(
    source_id: UUID,
    repository: SourceRepository = Depends(get_source_repository),
) -> SourceRead:
    try:
        return repository.get(source_id)
    except SourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source introuvable.",
        ) from error

@app.get(
    "/api/sources/{source_id}/pages",
    response_model=list[SourcePageRead],
    tags=["sources"],
)
def list_source_pages(
    source_id: UUID,
    repository: SourceRepository = Depends(get_source_repository),
) -> list[SourcePageRead]:
    try:
        return repository.list_pages(source_id)
    except SourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source introuvable.",
        ) from error

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

@app.post(
    "/api/corpora/{corpus_id}/sources/pdf",
    response_model=SourceRead,
    status_code=status.HTTP_201_CREATED,
    tags=["sources"],
)
async def upload_pdf_source(
    corpus_id: UUID,
    file: UploadFile = File(...),
    service: PdfSourceService = Depends(get_pdf_source_service),
) -> SourceRead:
    content = await file.read()

    try:
        return service.upload(
            corpus_id=corpus_id,
            original_filename=file.filename or "document.pdf",
            content_type=file.content_type or "",
            content=content,
        )
    except CorpusNotFoundForSourceError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corpus introuvable.",
        ) from error
    except EmptyFileError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier est vide.",
        ) from error
    except FileTooLargeError as error:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Le fichier dépasse la taille maximale autorisée.",
        ) from error
    except InvalidPdfError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier fourni n’est pas un PDF valide.",
        ) from error
    finally:
        await file.close()

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

