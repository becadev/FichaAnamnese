"""Base declarativa e acesso ao banco.

A `Base` é **única** (F0-T2): com duas, cada model cairia num registry separado
e os `relationship` entre eles nunca se resolveriam.

Engine e sessão nascem sob demanda para que `import app.main` não exija banco
configurado — o que mantém o pacote importável em CI e nos testes de unidade.
O resto da camada (`get_db`, tuning de pool) é da F0-T5.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os models."""


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Engine do processo. `pool_pre_ping` descarta conexão morta pelo Neon."""
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_sessionmaker() -> sessionmaker[Session]:
    """Fábrica de sessões ligada ao engine do processo."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
