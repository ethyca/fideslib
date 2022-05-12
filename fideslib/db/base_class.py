from __future__ import annotations

from typing import Any
from uuid import uuid4

from fideslang.models import FidesKey  # type: ignore
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql import func

from fideslib.exceptions import KeyOrNameAlreadyExists, KeyValidationError
from fideslib.utils.text import to_snake_case


def get_key_from_data(data: dict[str, Any], cls_name: str) -> str:
    """Extracts key from data, validates.

    If no key, uses a snake-cased name. Will be used as the URL onupdate
    applicable classes.
    """
    key = FidesKey.validate(data.get("key")) if data.get("key") else None
    if key is None:
        name = data.get("name")
        if name is None:
            raise KeyValidationError(f"{cls_name} requires a name.")
        key = FidesKey.validate(to_snake_case(name))
    return key


class FidesBase:
    """
    A generic base class to be used for all DB models, automatically adding the
    following fields to every table:
    - id: a UUID
    - created_at: the datetime that the record was created
    - updated_at: the datetime that the record was last updated
    """

    def generate_uuid(self) -> str:
        """
        Generates a uuid with a prefix based on the tablename to be used as the
        record's ID value
        """
        try:
            # `self` in this context is an instance of
            # sqlalchemy.dialects.postgresql.psycopg2.PGExecutionContext_psycopg2
            prefix = f"{self.current_column.table.name[:3]}_"  # type: ignore
        except AttributeError:
            # If the table name is unavailable for any reason, we don't
            # need to use it
            prefix = ""
        uuid = str(uuid4())
        return f"{prefix}{uuid}"

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=E0213
        """The name of this model's table in the DB"""
        return cls.__name__.lower()  # type: ignore #pylint: disable=E1101

    @declared_attr
    def id_field_path(cls) -> str:  # pylint: disable=E0213
        """
        The database path to any model's ID field, for use with ForeignKey
        specifications in the event we have overridden a model's
        __tablename__ attribute
        """
        return f"{cls.__tablename__}.id"

    id = Column(String(255), primary_key=True, index=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OrmWrappedFidesBase(FidesBase):
    """A wrapper class for our base model.

    This allows us to include the base model in type checking for our return types.
    This abstraction includes the following methods:
    - get(id): return the record at that particular ID
    - all(): return all records in that table
    - filter(conditions): return all records that satisfy filter conditions
    - create(data): create a record with provided data
    - update_from_class(conditions, values): update all records that match the filter
        conditions with the data inside values, called from the class
    - update: update the record related to the object calling this method
    - delete_with_class(id): delete the record at the provided ID, called from the class
    - delete: delete the record related to the object calling this method
    - delete_all: delete all records in this table
    - save: update the record related to the object calling this method with the current
        data stored on the object
    """

    __mapper_args__ = {"confirm_deleted_rows": False}
    # This line hides sql alchemy warnings of the form:
    # Sqlalchemy/orm/persistence.py:1461: SAWarning: DELETE statement on table
    # 'storageconfig' expected to delete 1 row(s); 0 were matched. Please set
    # confirm_deleted_rows=False within the mapper configuration to prevent this
    # warning.

    @classmethod
    def get_optional_field_names(cls) -> list[str]:
        """Returns the names of all nullable fields on the wrapped model"""
        return [
            field.name
            for field in list(cls.__table__.columns)  # type: ignore # pylint: disable=E1101
            if field.nullable
        ]

    @classmethod
    def get(cls, db: Session, *, id: Any) -> FidesBase | None:  # pylint: disable=W0622
        """Fetch a database record via a table ID"""
        return db.query(cls).get(id)

    @classmethod
    def get_by(
        cls,
        db: Session,
        *,
        field: str,
        value: str | int,
    ) -> list[FidesBase]:
        """Fetch a database record via a dynamic key, supplied at call time"""
        kwargs = {field: value}
        return db.query(cls).filter_by(**kwargs).first()  # type: ignore

    @classmethod
    def query(cls, db: Session) -> Query:
        """Create a blank query for the class"""
        return db.query(cls)

    @classmethod
    def all(cls, db: Session) -> list[OrmWrappedFidesBase]:  # pylint: disable=W0622
        """Fetch all database records in table"""
        return db.query(cls).all()

    @classmethod
    def filter(
        cls,
        db: Session,
        *,
        conditions: Any,  # TODO: What pydantic types are these? # pylint: disable=W0511
    ) -> Query:
        """Fetch multiple models from a database table"""
        return db.query(cls).filter(conditions)

    @classmethod
    def create(cls, db: Session, *, data: dict[str, Any]) -> FidesBase:
        """Create a new row in the database"""
        # Build properly formatted key for applicable classes
        if hasattr(cls, "key"):
            data["key"] = get_key_from_data(data, cls.__name__)
            if db.query(cls).filter_by(key=data["key"]).first():
                raise KeyOrNameAlreadyExists(
                    f"Key {data['key']} already exists in {cls.__name__}. Keys will be snake-cased names if not provided. "  # pylint: disable=C0301
                    f"If you are seeing this error without providing a key, please provide a key or a different name."  # pylint: disable=C0301
                    ""
                )

        if hasattr(cls, "name"):
            data["name"] = data.get("name", None)
            if db.query(cls).filter_by(name=data["name"]).first():
                raise KeyOrNameAlreadyExists(
                    f"Name {data['name']} already exists in {cls.__name__}."
                )

        # Create
        db_obj = cls(**data)  # type: ignore
        return cls.persist_obj(db, db_obj)

    @classmethod
    def get_by_key_or_id(
        cls, db: Session, *, data: dict[str, Any]
    ) -> FidesBase | list[FidesBase] | None:
        """Retrieves db object by id, if provided, otherwise attempts by key"""
        db_obj: FidesBase | list[FidesBase] | None = None
        if data.get("id") is not None:
            # If `id` has been included in `data`, preference that
            db_obj = cls.get(db=db, id=data["id"])
        elif data.get("key") is not None:
            # Otherwise, try with `key`
            db_obj = cls.get_by(db=db, field="key", value=data["key"])
        return db_obj

    @classmethod
    def create_or_update(
        cls, db: Session, *, data: dict[str, Any]
    ) -> FidesBase | list[FidesBase]:
        """Create an object, or update the existing version.

        There's an edge case where `data["id"]` and `data["key"]` can point attempt
        different records, in which case this method will attempt to update the
        fetched record with the key of another, and a `KeyOrNameAlreadyExists`
        error will be thrown. If neither `key`, nor `id` are passed in, leave
        `db_obj` as None and assume we are creating a new object.
        """
        db_obj = cls.get_by_key_or_id(db=db, data=data)
        if db_obj:
            db_obj.update(db=db, data=data)  # type: ignore
        else:
            db_obj = cls.create(db=db, data=data)
        return db_obj

    @classmethod
    def get_or_create(
        cls, db: Session, *, data: dict[str, Any]
    ) -> tuple[bool, FidesBase | None]:
        """Fetch an object, or create it if none is found"""
        db_obj = db.query(cls).filter_by(**data).first()
        created = False
        if not db_obj:
            db_obj = cls.create(db=db, data=data)  # type: ignore
            created = True
        return created, db_obj

    @classmethod
    def update_with_class(
        cls, db: Session, *, conditions: Any, values: dict[str, Any]
    ) -> int:
        """Update all objects within a filter at database level"""
        return db.query(cls).filter(conditions).update(values=values)

    @classmethod
    def delete_with_class(
        cls, db: Session, *, id: str  # pylint: disable=W0622
    ) -> FidesBase | None:
        """Delete an existing row from the database from the object's class"""
        obj = db.query(cls).get(id)
        if obj is None:
            return None
        db.delete(obj)
        db.commit()
        return obj

    @classmethod
    def delete_all(cls, db: Session) -> int:  # pylint: disable=W0622
        """Delete all rows in this table"""
        deleted_count = db.query(cls).delete()
        return deleted_count

    def refresh_from_db(self, db: Session) -> FidesBase:
        """Returns a current version of this object from the database"""
        return db.query(self.__class__).get(self.id)

    def update(self, db: Session, *, data: dict[str, Any]) -> FidesBase:
        """Update specific row with supplied values"""
        # Set self.key where applicable
        if hasattr(self, "key") and "key" in data:
            data["key"] = get_key_from_data(data, self.__class__.__name__)

        # Update dataset with values in data
        for key, val in data.items():
            setattr(self, key, val)

        return self.save(db=db)

    def delete(self, db: Session) -> FidesBase | None:
        """Delete an existing row in the database from an existing object in memory"""
        db.delete(self)
        db.commit()
        return self

    def save(self, db: Session) -> FidesBase:
        """Save the current object over an existing row in the database"""
        if hasattr(self, "key"):
            key = getattr(self, "key", "")

            is_valid = False
            if key is not None:
                valid_key_chars = (
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
                )
                to_validate = key
                for char in valid_key_chars:
                    to_validate = to_validate.replace(char, "")

                # Any invalid chars won't have been replaced above, so the length of our
                # validation var will still be >0
                is_valid = len(to_validate) == 0

            if not is_valid:
                raise KeyValidationError(
                    f"Key '{key}' on {self.__class__.__name__} is invalid."
                )

        return OrmWrappedFidesBase.persist_obj(db, self)

    @classmethod
    def persist_obj(cls, db: Session, resource: FidesBase) -> FidesBase:
        """Method to be run after 'create' or 'save' to write the resource to the db
        Can be overridden on subclasses to not commit immediately whencreating
        creating/updating.
        """
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource


Base = declarative_base(cls=OrmWrappedFidesBase)
