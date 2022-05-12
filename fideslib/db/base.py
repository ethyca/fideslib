# Import all the models, so that Base has them before being
# imported by Alembic
# pylint: disable=W0611
from fideslib.db.base_class import Base
from fideslib.models.fides_user import FidesUser
from fideslib.models.fides_user_permissions import FidesUserPermissions
