import pathlib
from redis.asyncio import Redis
from aiohttp_session import session_middleware, get_session
from aiohttp_session.redis_storage import RedisStorage

from database import async_db_session
from users.models import User

BASE_DIR = pathlib.Path(__file__).parent

redis_pool = Redis(host="localhost", port=6379)


async def request_user_middleware(app, handler):
    async def middleware(request):
        # Создаем атрибут session
        # Импортируем from aiohttp_session import get_session
        request.session = await get_session(request)

        # !!!!!!!!!!!!!!!!!!!
        # Создаем пользователя
        request.user = None

        # Из сессии получаем ID пользователя в БД
        user_id = request.session.get('user_id')

        if user_id is not None:
            # Нашли ID пользователя
            request.user = await User.get(id=user_id)

        # Вызываем представление
        return await handler(request)

    return middleware


MIDDLEWARES = [
    session_middleware(RedisStorage(redis_pool)),
    request_user_middleware
]


async def init_db(app):
    await async_db_session.init()
