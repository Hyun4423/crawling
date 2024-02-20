"""
ASGI config for crawling project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from uvicorn import run

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crawling.settings')

application = get_asgi_application()

if __name__ == "__main__":
    run(application, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
