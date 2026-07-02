from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from uuid import UUID

from .database import get_database_session
from fastapi.middleware.cors import CORSMiddleware

from .repository import AgentNotFoundError, AgentRepository
from .corpus_repository import (
    AgentNotFoundForCorpusError,
    CorpusNotFoundError,
    CorpusRepository,
)
from .schemas import (
    AgentCreate,
    AgentRead,
    AgentUpdate,
    CorpusCreate,
    CorpusRead,
    CorpusSearchRequest,
    CorpusSearchResult,
    SourceChunkRead,
    SourcePageRead,
    SourceRead,
    CorpusAnswerRequest,
    CorpusAnswerResponse,
    CorpusAnswerSourceRead,
)
from .config import get_settings
from .document_storage import LocalDocumentStorage
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
from .source_chunk_service import (
    SourceChunkService,
    SourceHasNoExtractedPagesError,
)
from .chunk_embedding_repository import ChunkEmbeddingRepository
from .embedding_client import (
    EmbeddingProviderError,
    MissingEmbeddingApiKeyError,
    OpenAIEmbeddingClient,
)
from .source_chunk_embedding_service import (
    SourceChunkEmbeddingService,
    SourceHasNoChunksError,
)
from .corpus_search_service import CorpusSearchService
from .vector_search_repository import (
    CorpusNotFoundForSearchError,
    VectorSearchRepository,
)
from .openai_answer_adapter import (
    AnswerGenerationError,
    MissingAnswerGenerationApiKeyError,
    OpenAIAnswerGenerationAdapter,
)
from .rag_answer_service import NoRelevantContextError, RagAnswerService

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

def get_source_chunk_service(
    repository: SourceRepository = Depends(get_source_repository),
) -> SourceChunkService:
    return SourceChunkService(repository=repository)

def get_source_chunk_embedding_service(
    session: Session = Depends(get_database_session),
) -> SourceChunkEmbeddingService:
    settings = get_settings()

    return SourceChunkEmbeddingService(
        source_repository=SourceRepository(session),
        embedding_repository=ChunkEmbeddingRepository(session),
        embedding_client=OpenAIEmbeddingClient(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        ),
    )

def get_corpus_search_service(
    session: Session = Depends(get_database_session),
) -> CorpusSearchService:
    settings = get_settings()

    return CorpusSearchService(
        vector_search_repository=VectorSearchRepository(session),
        embedding_client=OpenAIEmbeddingClient(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        ),
    )

def get_rag_answer_service(
    session: Session = Depends(get_database_session),
) -> RagAnswerService:
    settings = get_settings()

    corpus_search_service = CorpusSearchService(
        vector_search_repository=VectorSearchRepository(session),
        embedding_client=OpenAIEmbeddingClient(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        ),
    )

    return RagAnswerService(
        corpus_search_service=corpus_search_service,
        answer_generation_client=OpenAIAnswerGenerationAdapter(
            api_key=settings.openai_api_key,
            model=settings.answer_model,
        ),
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

@app.post(
    "/api/sources/{source_id}/chunks",
    response_model=list[SourceChunkRead],
    status_code=status.HTTP_201_CREATED,
    tags=["sources"],
)
def generate_source_chunks(
    source_id: UUID,
    service: SourceChunkService = Depends(get_source_chunk_service),
) -> list[SourceChunkRead]:
    try:
        return service.generate_for_source(source_id)
    except SourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source introuvable.",
        ) from error
    except SourceHasNoExtractedPagesError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La source ne contient aucune page extraite.",
        ) from error


@app.get(
    "/api/sources/{source_id}/chunks",
    response_model=list[SourceChunkRead],
    tags=["sources"],
)
def list_source_chunks(
    source_id: UUID,
    repository: SourceRepository = Depends(get_source_repository),
) -> list[SourceChunkRead]:
    try:
        return repository.list_chunks(source_id)
    except SourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source introuvable.",
        ) from error

@app.post(
    "/api/sources/{source_id}/embeddings",
    status_code=status.HTTP_201_CREATED,
    tags=["sources"],
)
def generate_source_chunk_embeddings(
    source_id: UUID,
    service: SourceChunkEmbeddingService = Depends(
        get_source_chunk_embedding_service
    ),
) -> dict[str, int]:
    try:
        embeddings = service.generate_for_source(source_id)
    except SourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source introuvable.",
        ) from error
    except SourceHasNoChunksError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La source ne contient aucun chunk à vectoriser.",
        ) from error
    except MissingEmbeddingApiKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La clé API d'embedding n'est pas configurée.",
        ) from error

    return {"created": len(embeddings)}

@app.post(
    "/api/corpora/{corpus_id}/search",
    response_model=list[CorpusSearchResult],
    tags=["corpora"],
)
def search_corpus_chunks(
    corpus_id: UUID,
    search_request: CorpusSearchRequest,
    service: CorpusSearchService = Depends(get_corpus_search_service),
) -> list[CorpusSearchResult]:
    try:
        return service.search(
            corpus_id=corpus_id,
            query=search_request.query,
            limit=search_request.limit,
        )
    except CorpusNotFoundForSearchError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corpus introuvable.",
        ) from error
    except MissingEmbeddingApiKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La clé API d'embedding n'est pas configurée.",
        ) from error
    except EmbeddingProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Le fournisseur d'embedding a échoué.",
        ) from error

@app.post(
    "/api/corpora/{corpus_id}/answer",
    response_model=CorpusAnswerResponse,
    tags=["corpora"],
)
def answer_corpus_question(
    corpus_id: UUID,
    answer_request: CorpusAnswerRequest,
    service: RagAnswerService = Depends(get_rag_answer_service),
) -> CorpusAnswerResponse:
    try:
        rag_answer = service.answer(
            corpus_id=corpus_id,
            question=answer_request.question,
            limit=answer_request.limit,
        )
    except CorpusNotFoundForSearchError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corpus introuvable.",
        ) from error
    except NoRelevantContextError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun contexte pertinent trouvé.",
        ) from error
    except (MissingEmbeddingApiKeyError, MissingAnswerGenerationApiKeyError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La clé API du fournisseur IA n'est pas configurée.",
        ) from error
    except (EmbeddingProviderError, AnswerGenerationError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Le fournisseur IA a échoué.",
        ) from error

    return CorpusAnswerResponse(
        answer=rag_answer.answer,
        sources=[
            CorpusAnswerSourceRead(
                chunk_id=source.chunk_id,
                source_id=source.source_id,
                page_number=source.page_number,
                text=source.text,
                score=source.score,
            )
            for source in rag_answer.sources
        ],
    )