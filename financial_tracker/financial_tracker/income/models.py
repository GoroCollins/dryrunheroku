from django.db import models
from financial_tracker.currencies.models import Currency, ExchangeRate
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .mixins import CurrencyConversionMixin
User = settings.AUTH_USER_MODEL

# Create your models here.
class BaseIncome(models.Model, CurrencyConversionMixin):
    income_name = models.CharField(max_length=100, null=False, blank=False)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=False, blank=False)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    amount_lcy = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="%(class)s_created_by", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="%(class)s_modified_by", null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["income_name"]),
            models.Index(fields=["created_at"]),
        ]
        # CheckConstraint for non-negative amounts
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name="%(class)s_amount_gte_zero"),
            models.CheckConstraint(check=models.Q(amount_lcy__gte=0), name="%(class)s_amount_lcy_gte_zero"),
        ]
        ordering = ["-created_at"]
        get_latest_by = ['-created_at']

    def clean(self):
        super().clean()

        # Validate amount
        if self.amount < 0:
            raise ValidationError({"amount": "Amount must be a non-negative value."})

        # Validate currency
        if not self.currency:
            raise ValidationError({"currency": "A valid currency must be provided."})

        # Ensure local currency amount calculation
        # try:
        #     exchange_rate = ExchangeRate.objects.get(currency=self.currency)
        #     self.amount_lcy = self.amount * exchange_rate.rate
        # except ObjectDoesNotExist:
        #     raise ValidationError({"currency": f"No exchange rate found for currency {self.currency}"})

    def save(self, *args, **kwargs):
        self.amount_lcy = self.convert_to_lcy(self.amount, self.currency)
        self.full_clean()  # Perform validation before saving
        super().save(*args, **kwargs)

class EarnedIncome(BaseIncome):
    # salaries, side hustle, income from services offered, freelancing income
    class Meta(BaseIncome.Meta):
        verbose_name = "Earned Income"
        verbose_name_plural = "Earned Income"
class PortfolioIncome(BaseIncome):
    # amount of money that you get from your investment asset
    # income from stocks, dividends, bonds, and capital gains is categorized as portfolio income
    class Meta(BaseIncome.Meta):
        verbose_name = "Portfolio Income"
        verbose_name_plural = "Portfolio Income"


class PassiveIncome(BaseIncome):
     # money that you earn with minimal effort from the resources that you have invested in
    # examples:music royalties, owner’s equity, interest from savings accounts, and rent from your personal properties
    class Meta(BaseIncome.Meta):
        verbose_name = "Passive Income"
        verbose_name_plural = "Passive Income"
