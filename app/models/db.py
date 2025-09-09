from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)
    original_data = Column(Text, nullable=False)
    description = Column(Text)
    edit_prompt = Column(Text)
    results = Column(JSONB)
