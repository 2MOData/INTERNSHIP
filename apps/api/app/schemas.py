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