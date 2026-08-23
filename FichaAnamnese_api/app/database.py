from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL não foi configurada."
    )
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Os modelos anotam os relacionamentos no estilo antigo (`List["Usuario"]`, e não
# `Mapped[List["Usuario"]]`). Sem isto o SQLAlchemy 2.0 recusa a anotação e nem
# chega a montar a classe.
Base.__allow_unmapped__ = True