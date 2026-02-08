from django.apps import AppConfig


class SeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "seo"

    def ready(self):
        from .agents.client import configure_agent_client

        configure_agent_client()
