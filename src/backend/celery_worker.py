#!/usr/bin/env python
from server import celery, create_app

app = create_app()
app.app_context().push()
