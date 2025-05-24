from datetime import datetime, UTC
import uuid

from sqlalchemy import Column, DateTime, JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SyntheticDataRun(Base):
    """Model for tracking synthetic data generation runs."""

    __tablename__ = "synthetic_data_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    schema = Column(JSONB, nullable=False)  # Store the schema used for generation
    num_samples = Column(JSON, nullable=False)  # Number of samples generated
    status = Column(JSON, nullable=False)  # e.g., "completed", "failed", "in_progress"
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
