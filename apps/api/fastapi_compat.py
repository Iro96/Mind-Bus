import inspect
from dataclasses import dataclass
from types import SimpleNamespace

try:
    from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, UploadFile, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
except ImportError:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail=None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class _Status:
        HTTP_401_UNAUTHORIZED = 401
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_500_INTERNAL_SERVER_ERROR = 500
        HTTP_501_NOT_IMPLEMENTED = 501

    status = _Status()

    class Depends:
        def __init__(self, dependency=None):
            self.dependency = dependency

    class BackgroundTasks:
        def __init__(self):
            self.tasks = []

        def add_task(self, func, *args, **kwargs):
            self.tasks.append((func, args, kwargs))

        async def __call__(self):
            for func, args, kwargs in self.tasks:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    await result

    class APIRouter:
        def __init__(self, *args, **kwargs):
            self.routes = []
            self.args = args
            self.kwargs = kwargs

        def _register(self, method: str, path: str, **kwargs):
            def decorator(func):
                self.routes.append(
                    {
                        "method": method,
                        "path": path,
                        "endpoint": func,
                        "options": kwargs,
                    }
                )
                return func
            return decorator

        def get(self, path: str, **kwargs):
            return self._register("GET", path, **kwargs)

        def post(self, path: str, **kwargs):
            return self._register("POST", path, **kwargs)

    class FastAPI:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.routers = []

        def middleware(self, _middleware_type: str):
            def decorator(func):
                return func
            return decorator

        def include_router(self, router):
            self.routers.append(router)

        def on_event(self, _event_name: str):
            def decorator(func):
                return func
            return decorator

    class Request:
        def __init__(self, method: str = "GET", path: str = ""):
            self.method = method
            self.url = SimpleNamespace(path=path)

    @dataclass
    class HTTPAuthorizationCredentials:
        scheme: str = "Bearer"
        credentials: str = ""

    class HTTPBearer:
        def __call__(self):
            return HTTPAuthorizationCredentials()

    class UploadFile:
        def __init__(self, filename: str = "", file=None):
            self.filename = filename
            self.file = file

    def File(default):
        return default
