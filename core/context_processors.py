from .models import SiteSetting


def site_settings(request):
    """Expose the SiteSetting singleton to every template as `org`.

    Named `org` (not `site`) to avoid colliding with the `site` variable that
    Django's auth views (LoginView, PasswordResetView, ...) inject.
    """
    return {"org": SiteSetting.load()}
