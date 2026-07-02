from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AgentStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class AgentCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(default="", max_length=500)
    use_case: str = Field(min_length=3, max_length=200)
    language: str = Field(default="fr", pattern="^(fr|en)$")


class AgentRead(AgentCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    status: AgentStatus = AgentStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    use_case: str | None = Field(default=None, min_length=3, max_length=200)
    language: str | None = Field(default=None, pattern="^(fr|en)$")

class CorpusStatus(StrEnum):
    EMPTY = "empty"
    INDEXING = "indexing"
    READY = "ready"
    ERROR = "error"


class CorpusCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(default="", max_length=500)


class CorpusRead(CorpusCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agent_id: UUID
    status: CorpusStatus
    created_at: datetime
    updated_at: datetime

class SourceStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    corpus_id: UUID
    source_type: str
    original_filename: str
    content_type: str
    size_bytes: int
    status: SourceStatus
    created_at: datetime
    updated_at: datetime

class SourcePageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    page_number: int
    text: str
    created_at: datetime

class SourceChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    page_number: int
    chunk_index: int
    text: str
    created_at: datetime

class CorpusSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)


class CorpusSearchResult(BaseModel):
    chunk_id: UUID
    source_id: UUID
    page_number: int
    chunk_index: int
    text: str
    score: float