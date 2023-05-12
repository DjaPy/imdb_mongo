import asyncio
import time
import traceback
from http import HTTPStatus
from typing import Any, Awaitable, Optional

from aiomisc import Service
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import Counter, Gauge, Histogram
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Match
from uvicorn.config import Config

from src.base.fastapi_service.config import FastAPISettings
from src.base.fastapi_service.uvicorn_server import Server

from .problem import Problem, ProblemResponse


class FastAPIService(Service):

    HTTP_PANIC_RECOVERY_TOTAL = Counter(
        'http_panic_recovery_total',
        'Total number of recovered panics.',
        ['http_service', 'http_method', 'http_handler'],
    )
    HTTP_REQUEST_DURATION_SECONDS = Histogram(
        'http_request_duration_seconds',
        'The latency of the HTTP requests.',
        ['http_service', 'http_handler', 'http_method', 'http_code'],
        buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
    )
    HTTP_REQUESTS_INFLIGHT = Gauge(
        'http_requests_inflight',
        'The number of inflight requests being handled at the same time.',
        ['http_service', 'http_handler'],
    )
    HTTP_RESPONSE_SIZE_BYTES = Histogram(
        'http_response_size_bytes',
        'The size of the HTTP responses.',
        ['http_service', 'http_handler', 'http_method', 'http_code'],
        buckets=[100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000, 1_000_000_000]
    )

    def __init__(
        self,
        settings: FastAPISettings,
        app_name: str = ''
    ) -> None:
        super().__init__()
        self._settings = settings
        self.app_name = app_name
        self.__fastapi: FastAPI | None = None
        self.__task: Awaitable[Any] | None = None
        self.__server_main: Server | None = None

    async def start(self) -> Any:
        self.__fastapi = FastAPI(title=self.app_name)
        self.context['fastapi'] = self.__fastapi

        @self.__fastapi.middleware('http')
        async def prom_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
            start_time = time.time()

            http_handler = ''
            routes = next(filter(lambda x: isinstance(x, APIRoute) and x.matches(request.scope)[0] == Match.FULL,
                                 request.app.routes), None)
            if routes:
                http_handler = routes.path

            self.HTTP_REQUESTS_INFLIGHT.labels(self.app_name, http_handler).inc()

            response: Response = await call_next(request)

            resp_time = time.time() - start_time
            self.HTTP_REQUEST_DURATION_SECONDS.labels(
                self.app_name, http_handler, request.method, response.status_code
            ).observe(resp_time)
            self.HTTP_RESPONSE_SIZE_BYTES.labels(
                self.app_name, http_handler, request.method, response.status_code
            ).observe(int(response.headers.get('content-length', 0)))
            self.HTTP_REQUESTS_INFLIGHT.labels(self.app_name, http_handler).dec()

            return response

        # RFC7807 Problem Details for HTTP APIs https://datatracker.ietf.org/doc/html/rfc7807
        @self.__fastapi.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ProblemResponse:
            status_ = HTTPStatus.BAD_REQUEST
            problem = Problem(title=status_.phrase, status=status_, instance=request.url.path,
                              invalid_params=exc.errors())

            return ProblemResponse(content=problem)

        # RFC7807 Problem Details for HTTP APIs https://datatracker.ietf.org/doc/html/rfc7807
        @self.__fastapi.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException) -> ProblemResponse:
            status_ = HTTPStatus(exc.status_code)
            detail = exc.detail if exc.detail != status_.phrase else None
            problem = Problem(title=status_.phrase, status=status_, detail=detail, instance=request.url.path)

            self.HTTP_PANIC_RECOVERY_TOTAL.labels(self.app_name, request.url.path, request.method).inc()

            return ProblemResponse(content=problem)

        # RFC7807 Problem Details for HTTP APIs https://datatracker.ietf.org/doc/html/rfc7807
        @self.__fastapi.exception_handler(Exception)
        async def debug_exception_handler(request: Request, exc: Any) -> ProblemResponse:
            status_ = HTTPStatus.INTERNAL_SERVER_ERROR
            detail = traceback.format_exception(exc, value=exc, tb=exc.__traceback__)
            problem = Problem(title=status_.phrase, status=status_, detail=detail, instance=request.url.path)

            return ProblemResponse(content=problem)

        FastAPIInstrumentor.instrument_app(self.__fastapi, tracer_provider=trace.get_tracer_provider())

        # https://github.com/encode/uvicorn/issues/541
        # https://stackoverflow.com/questions/23313720/asyncio-how-can-coroutines-be-used-in-signal-handlers
        # https://stackoverflow.com/questions/44850701/multiple-aiohttp-applications-running-in-the-same-process

        self.__server_main = Server(Config(  # pylint: disable=unexpected-keyword-arg
            app=self.__fastapi,
            host=self._settings.host,
            port=self._settings.port,
            workers=self._settings.uvicorn_workers,
            log_config=None,
        ))
        self.__task = asyncio.create_task(self.__server_main.serve())

    async def stop(self, exception: Optional[Exception] = None) -> Any:
        if self.__server_main:
            self.__server_main.set_should_exit()
            await self.__task  # type: ignore

    @property
    def fastapi(self) -> Optional[FastAPI]:
        return self.__fastapi
