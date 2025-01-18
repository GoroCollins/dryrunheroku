from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IncomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financial_tracker.income'
    verbose_name = _("Income")
