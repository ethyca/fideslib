from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker

from fideslib.core.config import FidesConfig
from fideslib.exceptions import MissingConfig

logger = logging.getLogger(__name__)


def get_db_engine(database_uri: str | URL) -> Engine:
    """Return a database engine."""
    return create_engine(database_uri, pool_pre_ping=True)


def get_db_session(
    config: FidesConfig,
    autocommit: bool = False,
    autoflush: bool = False,
    engine: Engine | None = None,
) -> sessionmaker:
    """Return a database SessionLocal."""
    if not config.database.SQLALCHEMY_DATABASE_URI:
        raise MissingConfig("No database uri available in the config")

    return sessionmaker(
        autocommit=autocommit,
        autoflush=autoflush,
        bind=engine or get_db_engine(config.database.SQLALCHEMY_DATABASE_URI),
        class_=ExtendedSession,
    )


class ExtendedSession(Session):
    """This class wraps the SQLAlchemy Session to provide some error handling on
    commits."""

    def commit(self) -> None:
        """Provide the option to automatically rollback failed transactions."""
        try:
            return super().commit()
        except Exception as exc:
            logger.error("Exception: %s", exc)
            # Rollback the current transaction after each failed commit
            self.rollback()
            raise
