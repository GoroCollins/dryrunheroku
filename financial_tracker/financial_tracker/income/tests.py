from django.test import TestCase
from currencies.models import Currency, ExchangeRate
from decimal import Decimal
from income.mixins import CurrencyConversionMixin

class CurrencyConversionMixinTest(TestCase):
    def setUp(self):
        # Set up a test currency and exchange rate
        self.currency = Currency.objects.create(code="USD", name="US Dollar")
        self.mixin = CurrencyConversionMixin()

    def test_conversion_valid_rate(self):
        # Create a valid exchange rate
        ExchangeRate.objects.create(currency=self.currency, rate=Decimal("1.2"))

        # Test the conversion with a valid rate
        result = self.mixin.convert_to_lcy(Decimal("100.00"), self.currency)
        self.assertEqual(result, Decimal("120.00"))

    def test_conversion_missing_rate(self):
        # Test conversion when no exchange rate exists
        new_currency = Currency.objects.create(code="EUR", name="Euro")

        with self.assertRaises(ValueError) as context:
            self.mixin.convert_to_lcy(Decimal("100.00"), new_currency)
        
        # Check the error message
        self.assertEqual(str(context.exception), f"No exchange rate found for currency {new_currency}")
