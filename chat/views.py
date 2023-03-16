from datetime import datetime

import aiohttp_jinja2
from aiohttp import web, WSMsgType, WSMessage

from extra import redirect, login_required
from .models import Room, Message


class HomeView(web.View):

    @aiohttp_jinja2.template("home.html")
    async def get(self):
        if self.request.user:
            rooms = await Room.all_rooms()
            print(rooms)
            return {"chat_rooms": rooms}

        return {}


class CreateRoom(web.View):

    @login_required
    @aiohttp_jinja2.template("chat/rooms.html")
    async def get(self):
        return {"chat_rooms": await Room.all_rooms()}

    @login_required
    async def post(self):
        post_data = await self.request.post()

        if not post_data.get("roomname"):
            redirect(self.request, "create_room")

        room_name = post_data["roomname"]
        try:
            # Если такая комната уже есть
            await Room.get(name=room_name)
            # Переходим в комнату для общения
            redirect(self.request, "room", name=room_name)
        except:
            pass

        # Комнаты такой еще нет
        await Room.create(name=room_name)
        # Переходим в комнату для общения
        redirect(self.request, "room", name=room_name)


class ChatRoom(web.View):

    @login_required
    @aiohttp_jinja2.template("chat/chat.html")
    async def get(self):
        room_name = self.request.match_info["name"]
        try:
            room: Room = await Room.get(name=room_name)
        except:
            redirect(self.request, "home")

        return {
            "chat_rooms": await Room.all_rooms(),
            "room": room,
            "room_messages": await room.all_messages()
        }


class WebSocket(web.View):

    async def get(self):
        room_name = self.request.match_info['name']

        # Объявим атрибут room
        self.room = await Room.get(name=room_name)
        self.user = self.request.user

        # "Укорачиваем" название переменной `app`
        app = self.request.app

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        if self.room.id not in app.wslist:
            # Если в комнате никто не находился до этого момента.
            # Создаем комнату.
            app.wslist[self.room.id] = {}

        user_id = self.user.id
        room_id = self.room.id

        # Добавляем в комнату текущего пользователя и его WS
        app.wslist[self.room.id][self.user.username] = ws

        # Ожидаем входящие данные
        async for msg in ws:
            msg: WSMessage

            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()

                else:

                    # Очищаем от лишних пробелов сообщение
                    # msg.data - переданное сообщение от пользователя
                    text = msg.data.strip()

                    # Добавляем в БД
                    message: Message = await Message.create(
                        room_id=room_id, user_id=user_id, text=text, created_at=datetime.now()
                    )

                    await self.broadcast(message, room_id)

            elif msg.type == web.WSMsgType.error:
                app.logger.debug(f'Connection closed with exception {ws.exception()}')

        await self.disconnect(self.user.username, room_id, ws)
        return ws

    async def broadcast(self, message, room_id):
        """ Send messages to all in this room """

        # Пользователи в комнате
        clients: dict = self.request.app.wslist[room_id]

        # Каждому пользователю в комнате отправляется сообщение
        for peer in clients:
            ws = clients[peer]
            await ws.send_json(await message.as_dict())

    async def disconnect(self, username, room_id, socket):
        """ Close connection and notify broadcast """
        self.request.app.wslist[room_id].pop(username, None)
        if not socket.closed:
            await socket.close()
