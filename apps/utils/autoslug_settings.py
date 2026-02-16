"""
Custom autoslug settings to use our custom slugify function
"""
from django.conf import settings
from django.urls import get_callable

# Use our custom slugify function
slugify_function_path = 'apps.utils.slugify.slugify'
slugify = get_callable(slugify_function_path)

# Enable modeltranslation support
autoslug_modeltranslation_enable = getattr(settings, 'AUTOSLUG_MODELTRANSLATION_ENABLE', False)