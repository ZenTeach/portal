"""Development entry point.

Runs the FastAPI app with uvicorn. The legacy version ran the Flask dev server
via ``create_app(True)``; that is superseded by the ASGI app.
"""

import os

from server.fastapi_app import app

sentry_dsn_key = os.environ.get("SENTRY_DSN")
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

    sentry_sdk.init(dsn=sentry_dsn_key)
    app = SentryAsgiMiddleware(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
