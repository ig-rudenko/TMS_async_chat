from aiohttp import web


def redirect(request, route_name: str, **kwargs):
    url: str = request.app.router[route_name].url_for(**kwargs)
    raise web.HTTPFound(url)


def login_required(function):
    async def wrapper(self, *args, **kwargs):
        if self.request.user is None:
            redirect(self.request, "login")
        return await function(self, *args, **kwargs)

    return wrapper
