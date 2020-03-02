#!/usr/bin/env python
import os
from server import celery, create_app

sentry_dsn_key = os.environ.get('SENTRY_DSN')
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=sentry_dsn_key,
        integrations=[CeleryIntegration()]
    )

app = create_app()
app.app_context().push()
