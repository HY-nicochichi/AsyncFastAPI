from typing import Annotated
from typing import Callable
from os import getenv
from uuid import (
    UUID,
    uuid7
)
from datetime import (
    datetime,
    UTC
)
from fastapi import Depends
from sqlalchemy import (
    ScalarResult,
    Select,
    select
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)

class Base(DeclarativeBase):
    __abstract__ = True
    id : Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)
    created: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    updated: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self) -> dict:
        dictionary: dict = self.__dict__.copy()
        dictionary.pop('_sa_instance_state')
        return dictionary

async_engine = create_async_engine(
    getenv('SQLALCHEMY_DATABASE_URI'),
    echo=False,
    pool_size=10,
    max_overflow=0,
    pool_pre_ping=False
)

create_async_session = async_sessionmaker(
    async_engine,
    autoflush=False,
    expire_on_commit=False
)

async def async_db_session():
    async with create_async_session() as async_session:
        async with async_session.begin():
            yield async_session

AsyncDBSession = Annotated[AsyncSession, Depends(async_db_session)]

class Repository[Model: Base]:
    def __init__(self, session: AsyncDBSession, model: type[Model]) -> None:
        self.session = session
        self.model = model

    async def all(self, *args: Callable[[Select], Select]) -> list[Model]:
        statement: Select = select(self.model)
        for arg in args:
            statement = arg(statement)
        scalar_result: ScalarResult[Model] = await self.session.scalars(statement)
        return scalar_result.all()

    async def find_by(self, **kwargs) -> Model|None:
        scalar_result: ScalarResult[Model] = await self.session.scalars(
            select(self.model).filter_by(**kwargs)
        )
        return scalar_result.one_or_none()

    async def create(self, **kwargs) -> Model:
        instance: Model = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: Model, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(instance, key, val)
        await self.session.flush()

    async def delete(self, instance: Model) -> None:
        await self.session.delete(instance)
        await self.session.flush()

def get_repository[Model: Base](model: type[Model]) -> Callable:
    def _get_repository(session: AsyncDBSession) -> Repository[Model]:
        return Repository(session, model)
    return _get_repository
