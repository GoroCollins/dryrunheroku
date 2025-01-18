from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal
User = settings.AUTH_USER_MODEL

# Create your models here.
class Currency(models.Model):
    code = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(r"^[A-Z]{3}$", "Currency code must be 3 uppercase letters.")
        ],
        primary_key=True
    )
    description = models.CharField(max_length=100, null=False, blank=False)
    is_local = models.BooleanField(null=False, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='ccreator', related_query_name='ccreator'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='cmodifier', related_query_name='cmodifier', blank=True, null=True
    )
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.code} - {self.description}'

    def clean(self):
        if self.is_local and Currency.objects.exclude(pk=self.pk).filter(is_local=True).exists():
            raise ValidationError("Only one local currency is allowed.")
        if not self.is_local and not Currency.objects.filter(is_local=True).exists():
            raise ValidationError("Cannot set this currency as foreign; no local currency exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_local"],
                condition=models.Q(is_local=True),
                name="unique_local_currency"
            )
        ]
        indexes = [
            models.Index(fields=["is_local"]),
            models.Index(fields=["code"])
        ]
        verbose_name_plural = "Currencies"

class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='currency', related_query_name='currency', blank=False, null=False)
    rate = models.DecimalField(
    max_digits=8,
    decimal_places=2,
    validators=[MinValueValidator(Decimal(0.1))])
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ercreator', related_query_name='ercreator')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ermodifier', related_query_name='ermodifier', blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    # def __str__(self) -> str:
    #     return f"Exchange rate for {self.currency} as at {self.created_at.strftime('%I:%M:%S %p')} on {self.created_at.strftime('%B')}, {self.created_at.strftime('%d')}, {self.created_at.strftime('%Y')}"
    
    def __str__(self) -> str:
        return f"Exchange rate for {self.currency.code} on {self.created_at:%B %d, %Y at %I:%M %p}"
    def clean(self):
        """Ensure that the currency is not local."""
        if self.currency.is_local:
            raise ValidationError("Exchange rates cannot be assigned to a local currency.")

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()  # This calls `clean()` method
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["currency"]),
            models.Index(fields=["rate"]),
        ]
        ordering = ["-created_at"]
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"