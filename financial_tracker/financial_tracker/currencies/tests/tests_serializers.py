import pytest
from ..api.serializers import CurrencySerializer, ExchangeRateSerializer
from ..models import Currency, ExchangeRate
from rest_framework.exceptions import ValidationError
from django.utils.timezone import localtime

@pytest.mark.django_db
def test_currency_serializer_valid(currency_factory, user):
    #user = UserFactory(username="testuser")  # Assuming you have a `UserFactory`
    currency = currency_factory(is_local=True, created_by=user)
    serializer = CurrencySerializer(currency)
    created_at = localtime(currency.created_at).isoformat()
    modified_at = localtime(currency.modified_at).isoformat()
    expected_data = {
        "code": currency.code,
        "description": currency.description,
        "is_local": currency.is_local,
        "created_by": currency.created_by.username if currency.created_by else None,  # Expected username
        "created_at": created_at,
        "modified_by": currency.modified_by.username if currency.modified_by else None,  # Assuming `modified_by` is not set
        "modified_at": modified_at,
    }
    assert serializer.data == expected_data



@pytest.mark.django_db
def test_currency_serializer_validation(currency_factory):
    currency_factory(is_local=True)  # Existing local currency
    serializer = CurrencySerializer(data={"code": "EUR", "description": "Euro", "is_local": True})
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    assert "currency with this is local already exists." in str(excinfo.value)


@pytest.mark.django_db
def test_exchange_rate_serializer_valid(currency_factory, exchange_rate_factory, user):
    currency_factory(is_local=True)
    currency = currency_factory(is_local=False)
    exchange_rate = exchange_rate_factory(currency=currency, rate=1.25, created_by=user)
    serializer = ExchangeRateSerializer(exchange_rate)
    # Normalize timestamps to the local timezone
    created_at = localtime(exchange_rate.created_at).isoformat()
    modified_at = localtime(exchange_rate.modified_at).isoformat()
    expected_data = {
        "id": exchange_rate.id,
        "currency": currency.code,  # Use primary key for currency
        "currency_description": currency.description,
        "currency_is_local": str(currency.is_local),  # Match the serializer's output
        "rate": str(exchange_rate.rate),
        "created_by": exchange_rate.created_by.username if exchange_rate.created_by else None,  # Expected username
        "created_at": created_at,
        "modified_by": exchange_rate.modified_by.username if exchange_rate.modified_by else None, 
        "modified_at": modified_at,
    }
    assert serializer.data == expected_data


@pytest.mark.django_db
def test_exchange_rate_serializer_local_currency(currency_factory):
    # Create a local currency
    local_currency = currency_factory(is_local=True)

    # Attempt to create an exchange rate for the local currency
    serializer = ExchangeRateSerializer(data={"currency": local_currency.code, "rate": 1.25})
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    assert "Cannot assign exchange rates to the local currency." in str(excinfo.value)

