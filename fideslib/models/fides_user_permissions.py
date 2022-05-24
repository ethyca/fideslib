from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import backref, relationship

from fideslib.db.base_class import Base
from fideslib.models.fides_user import FidesUser
from fideslib.oauth.scopes import PRIVACY_REQUEST_READ


class FidesUserPermissions(Base):
    """The DB ORM model for FidesUserPermissions"""

    user_id = Column(String, ForeignKey(FidesUser.id), nullable=False, unique=True)
    # escaping curly braces requires doubling them. Not a "\". So {{{test123}}}
    # renders as {test123}
    scopes = Column(
        ARRAY(String), nullable=False, default=f"{{{PRIVACY_REQUEST_READ}}}"
    )
    user = relationship(
        FidesUser,
        backref=backref("permissions", cascade="all,delete", uselist=False),
    )
