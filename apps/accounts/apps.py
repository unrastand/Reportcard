from django.apps import AppConfig


class AccountsConfig(AppConfig):
    # overriding app name and label to avoid conflict with 
    name = 'apps.accounts'
    
    def ready(self):
        from . import signals
