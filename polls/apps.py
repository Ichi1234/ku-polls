"""
This module contains the application configuration for the 'polls' app.

Django uses AppConfig classes to represent application configurations,
allowing custom initialization and setup of the app.
"""

from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Configuration class for the 'polls' application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
