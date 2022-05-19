from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)


def get_db_engine(database_uri: str | URL) -> Engine:
    """Return a database engine."""
    return create_engine(database_uri, pool_pre_ping=True)


def get_db_session(
    engine: Engine,
    autocommit: bool = False,
    autoflush: bool = False,
) -> sessionmaker:
    """Return a database SessionLocal"""
    return sessionmaker(
        autocommit=autocommit,
        autoflush=autoflush,
        bind=engine,
        class_=ExtendedSession,
    )


class ExtendedSession(Session):
    """This class wraps the SQLAlchemy Session to provide some error handling
    on commits."""

    def commit(self) -> None:
        """Provide the option to automatically rollback failed transactions."""
        try:
            return super().commit()
        except Exception as exc:
            logger.error("Exception: %s", exc)
            # Rollback the current transaction after each failed commit
            self.rollback()
            raise
