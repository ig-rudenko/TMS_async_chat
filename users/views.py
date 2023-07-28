import datetime
import re
import hashlib
import os
import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_session import Session

from extra import redirect, login_required
from .models import User


class LogIn(web.View):

    @aiohttp_jinja2.template("users/login.html")
    async def get(self):
        return {}

    async def post(self):
        data = await self.request.post()
        username = data.get('username', '').lower()
        # password_user = data.get('password')

        # try:
        #     user = await User.get(username=username)
        # except Exception:
        #     print("Проверьте логин")
        #     redirect(self.request, "login")
        #     return
        # try:
        #     password = await user.password
        #     salt_from_password = password[:16]
        #     new_password = hashlib.pbkdf2_hmac('sha256', password_user.encode('utf-8'), salt_from_password, 100000)
        #     new_password == password
        # except Exception:
        #     print("Неправильный пароль")
        #     redirect(self.request, "login")

        else:
            self.login(user)
        return web.json_response({"user": user.id})

    def login(self, user: User):

        self.request.session["user_id"] = user.id
        self.request.session["time"] = str(datetime.datetime.now())

        redirect(self.request, "home")


class Register(web.View):

    @aiohttp_jinja2.template("users/register.html")
    async def get(self):
        print(self.request)

    async def check_username(self) -> str:
        """ Get username from post data, and check is correct """
        data = await self.request.post()
        username = data.get('username', '').lower()
        if not re.match(r'^[a-z]\w{0,9}$', username):
            return ""
        return username

    # async def check_password(self) -> str:
    #     data = await self.request.post()
    #     password = data.get('password')
    #     if len(password) < 6:
    #         return ""
    #     return password

    def login(self, user: User):
        self.request.session["user_id"] = user.id
        self.request.session["time"] = str(datetime.datetime.now())

        redirect(self.request, "home")

    async def post(self):
        username = await self.check_username()
        print('username', username)
        # password = await self.check_password()
        # print('password', password)


        if not username and password:
            redirect(self.request, "register")

        try:
            await User.get(username=username)
            # Такой пользователь уже есть!
            redirect(self.request, "login")
        except:
            print("Пользователя нет!")

        # salt = os.urandom(16)
        #
        # key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        # password = salt + key

        await User.create(username=username, password=password)
        user = await User.get(username=username, password=password)
        self.login(user)


class Logout(web.View):

    @login_required
    async def get(self):
        self.request.session.pop("user_id")
        redirect(self.request, "home")

