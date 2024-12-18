import urllib.request
import urllib.parse
import ssl

from django.contrib.sites.models import Site
from django.templatetags.static import static
from health_check.backends import BaseHealthCheckBackend

from config.settings import (
    HEALTH_CHECK_STATIC_FILE,
    HEALTH_CHECK_MEDIA_FILE,
    MEDIA_URL,
    STORAGE_MEDIA_BACKEND,
)


def check_or_add_host(url: str, media: bool = False) -> str:
    if url.startswith('https://') or url.startswith('http://'):
        return url
    if media and STORAGE_MEDIA_BACKEND == 's3':
        return 'https://' + url
    current_site = Site.objects.get_current()
    host = current_site.domain
    if not host.endswith('/') and not url.startswith('/'):
        url = f'https://{host}/{url}'
    else:
        url = f'https://{host}{url}'
    return url


class StaticHealthCheck(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self) -> None:
        url = check_or_add_host(static(HEALTH_CHECK_STATIC_FILE))
        try:
            with urllib.request.urlopen(
                    url=url,
                    context=ssl.SSLContext()) as _:
                pass
        except Exception as e:
            self.add_error(f'Failed to connect to {url}: {e}')

    def identifier(self) -> str:
        return self.__class__.__name__


class MediaHealthCheck(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self) -> None:
        url = check_or_add_host(
            MEDIA_URL + HEALTH_CHECK_MEDIA_FILE, media=True
        )
        try:
            with urllib.request.urlopen(
                    url=url,
                    context=ssl.SSLContext()) as _:
                pass
        except Exception as e:
            self.add_error(f'Failed to connect to {url}: {e}')

    def identifier(self) -> str:
        return self.__class__.__name__
