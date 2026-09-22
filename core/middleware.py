import os

from django.conf import settings as django_settings
from whitenoise.middleware import WhiteNoiseMiddleware


class MediaWhiteNoiseMiddleware(WhiteNoiseMiddleware):
    """Serve collected static files and uploaded media from Gunicorn.

    deploy.sh only proxies to Gunicorn. WhiteNoise is the file server for
    that process, including files written to MEDIA_ROOT after startup.
    """

    def __init__(self, get_response, settings=django_settings):
        super().__init__(get_response, settings)
        media_root = getattr(settings, "MEDIA_ROOT", None)
        media_url = getattr(settings, "MEDIA_URL", None)
        if media_root and media_url:
            os.makedirs(media_root, exist_ok=True)
            prefix = media_url if str(media_url).startswith("/") else f"/{media_url}"
            self.add_files(str(media_root), prefix=prefix)
