from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker

from fideslib.core.config import config

logger = logging.getLogger(__name__)


def get_db_engine(database_uri: str | URL | None = None) -> Engine:
    """
    Return a database engine.

    If the TESTING environment var is set the database engine returned will
    be connected to the test DB.
    """
    if (
        not database_uri
        and not config.database.SQLALCHEMY_DATABASE_URI
        and not config.database.SQLALCHEMY_TEST_DATABASE_URI
    ):
        raise ValueError("No database_uri was provided, or set in the config.")

    uri: str | URL

    if database_uri is None:
        # Don't override any database_uri explicitly passed in
        if config.is_test_mode:
            uri = str(config.database.SQLALCHEMY_TEST_DATABASE_URI)
        else:
            uri = str(config.database.SQLALCHEMY_DATABASE_URI)
    else:
        uri = database_uri

    return create_engine(uri, pool_pre_ping=True)


ENGINE = get_db_engine()


def get_db_session(
    autocommit: bool = False,
    autoflush: bool = False,
    engine: Engine | None = None,
) -> sessionmaker:
    """Return a database SessionLocal"""
    return sessionmaker(
        autocommit=autocommit,
        autoflush=autoflush,
        bind=engine or ENGINE,
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
