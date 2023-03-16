from aiohttp import web
from . import views

routes = [
    web.route("*", "/", views.HomeView, name="home"),
    web.route("*", "/chat/rooms", views.CreateRoom, name="create_room"),
    web.route("get", "/chat/room/{name}", views.ChatRoom, name="room"),
    web.route("get", "/ws/{name}", views.WebSocket, name="ws"),
]
