from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class AgentModel(Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    use_case: Mapped[str] = mapped_column(String(200))
    language: Mapped[str] = mapped_column(String(2), default="fr")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    corpora: Mapped[list["CorpusModel"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )

class CorpusModel(Base):
    __tablename__ = "corpora"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="empty")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    agent: Mapped["AgentModel"] = relationship(back_populates="corpora")
    sources: Mapped[list["SourceModel"]] = relationship(
        back_populates="corpus",
        cascade="all, delete-orphan",
    )

class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    corpus_id: Mapped[UUID] = mapped_column(
        ForeignKey("corpora.id", ondelete="CASCADE"),
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(20), default="pdf")
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int]
    storage_key: Mapped[str] = mapped_column(String(500), unique=True)
    status: Mapped[str] = mapped_column(String(30), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    corpus: Mapped["CorpusModel"] = relationship(back_populates="sources")
    pages: Mapped[list["SourcePageModel"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
        order_by="SourcePageModel.page_number",
    )

class SourcePageModel(Base):
    __tablename__ = "source_pages"
    __table_args__ = (UniqueConstraint("source_id", "page_number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    source: Mapped["SourceModel"] = relationship(back_populates="pages")