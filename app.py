from aiohttp import web
import jinja2
import aiohttp_jinja2
import settings
from users.urls import routes as user_routes
from chat.urls import routes as chat_routes

if __name__ == '__main__':
    # Настройка приложения
    app = web.Application(
        middlewares=settings.MIDDLEWARES
    )

    print(app.middlewares)
    # ======= ROUTES ==========
    app.add_routes(user_routes)
    app.add_routes(chat_routes)
    print(app.router)

    # Настройка Jinja2 (для шаблонов)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(settings.BASE_DIR / "templates"),
        context_processors=[
            aiohttp_jinja2.request_processor,
        ]
    )

    # Web Sockets пользователей
    # {
    #   "room1": { "username1": WS, "username2": WS },
    #   "room2": { "username3": WS, "username21": WS },
    #
    # }
    app.wslist = {}

    # ========= STATIC ================
    app.router.add_static(
        "/static/", settings.BASE_DIR / "static", name="static"
    )

    app.on_startup.append(
        settings.init_db
    )

    # СТАРТ
    web.run_app(app)
