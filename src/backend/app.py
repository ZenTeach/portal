import os
from server import create_app

app = create_app(True)

sentry_dsn_key = os.environ.get('SENTRY_DSN')
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
    sentry_sdk.init(
        dsn=sentry_dsn_key
    )
    app = SentryWsgiMiddleware(app)

if __name__ == '__main__':
    app.run()
