from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    All ORM models inherit from this base class.
    SQLAlchemy 2.0 style.
    """
    pass
