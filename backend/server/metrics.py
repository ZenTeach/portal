"""Prometheus metrics for the FastAPI application.

Replaces ``prometheus-flask-exporter`` (which required the Flask app) with a
plain ``prometheus_client`` setup. A small ASGI middleware counts HTTP requests
by method/path/status, and the ``/metrics`` endpoint exposes those counters plus
the default process/GC/platform collectors.

Gunicorn multi-worker deployments should set ``PROMETHEUS_MULTIPROC_DIR`` in the
environment before the worker process starts; ``prometheus_client`` then
switches to multiprocess mode automatically.
"""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the application",
    ["method", "path", "status_code"],
)


class MetricsMiddleware:
    """Count requests by method, matched route path, and response status."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        status_code_holder = {"status": 500}
        method = request.method

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code_holder["status"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            path = request.scope.get("route", None)
            path_template = getattr(path, "path", None) or request.url.path
            HTTP_REQUESTS.labels(
                method=method,
                path=path_template,
                status_code=str(status_code_holder["status"]),
            ).inc()


def metrics_endpoint(_: Request) -> Response:
    """Return the Prometheus text exposition for the process."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
