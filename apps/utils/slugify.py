"""
Custom slugify function to replace autoslug.utils.slugify
"""
from django.template.defaultfilters import slugify as django_slugify


def slugify(value):
    """Custom slugify function"""
    return django_slugify(value)