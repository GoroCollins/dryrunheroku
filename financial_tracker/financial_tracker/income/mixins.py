from financial_tracker.currencies.models import ExchangeRate
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import logging
logger = logging.getLogger(__name__)

class CurrencyConversionMixin:
    def convert_to_lcy(self, amount, currency):
        """
        Converts the given amount to the local currency using the exchange rate.
        If the currency is local, the amount is returned as-is.
        :param amount: Decimal, amount to convert.
        :param currency: Currency object, the foreign currency.
        :return: Decimal, converted amount in local currency.
        """
        if currency.is_local:
            # If the currency is local, no conversion is needed
            return amount
        else:
            try:
                exchange_rate = ExchangeRate.objects.get(currency=currency)
                return amount * exchange_rate.rate
            except ObjectDoesNotExist:
                # Log the error and raise a ValidationError
                logger.error(f"Missing exchange rate for currency {currency}")
                raise ValidationError({"currency": f"No exchange rate found for currency {currency}"})

