from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = "catalog"
    verbose_name = "Каталог"

    def ready(self):
        import catalog.signals  # ← подключаем signals
