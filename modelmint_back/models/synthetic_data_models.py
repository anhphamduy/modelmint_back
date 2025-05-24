import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RunStatus(str, Enum):
    """Enum for synthetic data run status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SyntheticDataRun(Base):
    """Model for tracking synthetic data generation runs."""

    __tablename__ = "synthetic_data_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    schema = Column(JSONB, nullable=False)  # Store the schema used for generation
    num_samples = Column(JSON, nullable=False)  # Number of samples generated
    status = Column(
        SQLAlchemyEnum(RunStatus), nullable=False, default=RunStatus.IN_PROGRESS
    )
    result_url = Column(String, nullable=True)  # URL to access the generated data

    # Relationship to synthetic data samples
    samples = relationship("SyntheticData", back_populates="run")

    def __repr__(self):
        return f"<SyntheticDataRun(id={self.id}, created_at={self.created_at}, status={self.status})>"


class SyntheticData(Base):
    """Model for storing synthetic data samples."""

    __tablename__ = "synthetic_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    data = Column(JSONB, nullable=False)
    run_id = Column(
        UUID(as_uuid=True), ForeignKey("synthetic_data_runs.id"), nullable=False
    )

    # Relationship to the generation run
    run = relationship("SyntheticDataRun", back_populates="samples")

    def __repr__(self):
        return f"<SyntheticData(id={self.id}, created_at={self.created_at})>"
