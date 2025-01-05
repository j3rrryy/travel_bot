import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.BIGINT, unique=True, nullable=False, primary_key=True)
    username = sa.Column(sa.VARCHAR, unique=True, nullable=False)
    age = sa.Column(sa.INTEGER, nullable=False)
    sex = sa.Column(sa.VARCHAR, nullable=False)
    latitude = sa.Column(sa.FLOAT)
    longitude = sa.Column(sa.FLOAT)
    city = sa.Column(sa.VARCHAR)
    country = sa.Column(sa.VARCHAR, nullable=False)
    currency = sa.Column(sa.VARCHAR, nullable=False)
    bio = sa.Column(sa.VARCHAR)
    trips = relationship("Trip", back_populates="user")
    notes = relationship("Note", back_populates="user")
    expenses = relationship("Expense", back_populates="user")

    def __str__(self) -> str:
        return f"<User: {self.id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class Trip(Base):
    __tablename__ = "trips"

    id = sa.Column(sa.BIGINT, unique=True, nullable=False, primary_key=True)
    username = sa.Column(
        sa.ForeignKey(User.username, ondelete="CASCADE"),
        nullable=False,
    )
    name = sa.Column(sa.VARCHAR, nullable=False)
    description = sa.Column(sa.VARCHAR)
    locations = sa.Column(postgresql.ARRAY(sa.JSON), default=[])
    friends = sa.Column(postgresql.ARRAY(sa.VARCHAR), default=[])
    user = relationship("User", back_populates="trips")
    notes = relationship("Note", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")

    def __str__(self) -> str:
        return f"<Trip: {self.id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class Note(Base):
    __tablename__ = "notes"

    id = sa.Column(sa.BIGINT, unique=True, nullable=False, primary_key=True)
    user_id = sa.Column(
        sa.ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
    )
    trip_id = sa.Column(
        sa.ForeignKey(Trip.id, ondelete="CASCADE"),
        nullable=False,
    )
    name = sa.Column(sa.VARCHAR, nullable=False)
    path = sa.Column(sa.VARCHAR, nullable=False)
    file_type = sa.Column(sa.VARCHAR, nullable=False)
    width = sa.Column(sa.INTEGER)
    height = sa.Column(sa.INTEGER)
    is_private = sa.Column(sa.BOOLEAN)
    user = relationship("User", back_populates="notes")
    trip = relationship("Trip", back_populates="notes")

    def __str__(self) -> str:
        return f"<Note: {self.id}, Trip: {self.trip_id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class Expense(Base):
    __tablename__ = "expenses"

    id = sa.Column(sa.BIGINT, unique=True, nullable=False, primary_key=True)
    username = sa.Column(
        sa.ForeignKey(User.username, ondelete="CASCADE"),
        nullable=False,
    )
    trip_id = sa.Column(sa.ForeignKey(Trip.id, ondelete="CASCADE"), nullable=False)
    name = sa.Column(sa.VARCHAR, nullable=False)
    cost = sa.Column(sa.FLOAT, nullable=False)
    currency = sa.Column(sa.VARCHAR, nullable=False)
    date = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
    debtors = sa.Column(postgresql.ARRAY(sa.VARCHAR), default=[])
    user = relationship("User", back_populates="expenses")
    trip = relationship("Trip", back_populates="expenses")

    def __str__(self) -> str:
        return f"<Expense: {self.id}, Trip: {self.trip_id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d
