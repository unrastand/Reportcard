import pkgutil
from allauth.account import migrations

print(list(name for _, name, _ in pkgutil.iter_modules(migrations.__path__)))
