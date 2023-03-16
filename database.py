from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import update as sqlalchemy_update, select


Base = declarative_base()


class AsyncDatabaseConnection:

    def __init__(self):
        self._session = None
        self._engine = None

    async def init(self):
        self._engine = create_async_engine(
            "sqlite+aiosqlite:///sqlite.db",
        )
        self._session = AsyncSession(self._engine)
        print("init database connection!!!")

    def __getattr__(self, item):
        return getattr(self._session, item)


async_db_session = AsyncDatabaseConnection()


class ModelManagerMixin:

    @classmethod
    async def create(cls, **kwargs):
        obj = cls(**kwargs)
        async_db_session.add(obj)
        await async_db_session.commit()
        await async_db_session.refresh(obj)
        return obj

    @classmethod
    async def update(cls, id_: int, **kwargs) -> None:
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id_)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await async_db_session.execute(query)
        await async_db_session.commit()

    @classmethod
    async def get(cls, **kwargs):
        # kwargs может быть:
        # {"id": 1}
        # {"username": "asd"}

        filter_ = [
            getattr(cls, param) == value
            for param, value in kwargs.items()
        ]

        query = select(cls).where(*filter_)

        result = await async_db_session.execute(query)
        print("async def get", cls.__name__, result)
        (result,) = result.one()
        return result

    @classmethod
    async def filter(cls, **kwargs) -> list:
        args = kwargs.popitem()
        query = select(cls).where(getattr(cls, args[0]) == args[1])
        result = await async_db_session.execute(query)
        return [r[0] for r in result]
