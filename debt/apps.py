from django.apps import AppConfig


class DebtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'debt'
    verbose_name = 'Qarz daftari'
    
    def ready(self):
        try:
            import debt.signals
        except ImportError:
            pass
