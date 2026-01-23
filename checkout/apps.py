from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checkout"

    def ready(self):
        # Run the signals module to attach the signal receivers
        import checkout.signals  # noqa: F401
