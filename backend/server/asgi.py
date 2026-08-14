"""ASGI entry point for the FastAPI backend.

Run with::

    uvicorn server.asgi:app --host 0.0.0.0 --port 5000
"""

from server.fastapi_app import app  # noqa: F401
