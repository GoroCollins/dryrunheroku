# tests_models.py
import pytest
from ..models import Currency, ExchangeRate
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_create_local_currency(currency_factory, user):
    """Test creating a local currency."""
    local_currency = currency_factory(is_local=True, created_by=user)
    assert local_currency.is_local
    assert local_currency.created_by == user
    assert Currency.objects.count() == 1

@pytest.mark.django_db
def test_prevent_multiple_local_currencies(currency_factory):
    """Ensure that only one local currency can exist."""
    currency_factory(is_local=True)
    with pytest.raises(ValidationError, match="Only one local currency is allowed."):
        currency_factory(code="EUR", is_local=True)


@pytest.mark.django_db
def test_update_currency_to_local(currency_factory):
    """Ensure a foreign currency cannot be updated to local if one already exists."""
    currency_factory(is_local=True)
    foreign_currency = currency_factory(is_local=False)
    foreign_currency.is_local = True
    with pytest.raises(ValidationError, match="Only one local currency is allowed."):
        foreign_currency.save()


@pytest.mark.django_db
def test_prevent_foreign_currency_without_local(currency_factory):
    """Ensure that a foreign currency cannot be created without a local currency."""
    with pytest.raises(ValidationError, match="Cannot set this currency as foreign; no local currency exists."):
        currency_factory(is_local=False)
        
@pytest.mark.django_db
def test_unique_constraint_on_local_currency(currency_factory):
    """Test that the database enforces the unique constraint on local currency."""
    currency_factory(is_local=True)
    with pytest.raises(ValidationError):
        currency_factory(is_local=True)
        
@pytest.mark.django_db
def test_currency_str_representation(currency_factory):
    """Test the __str__ method of the Currency model."""
    # Create a local currency first to satisfy the validation constraint
    currency_factory(is_local=True)
    
    # Create the foreign currency to test the string representation
    currency = currency_factory(description="United States Dollar", code="USD", is_local=False)
    assert str(currency) == "USD - United States Dollar"


@pytest.mark.django_db
def test_currency_indexes(currency_factory):
    """Ensure indexes are correctly applied."""
    currency = currency_factory(code="USD", is_local=True)
    assert Currency.objects.filter(code="USD").exists()
    assert Currency.objects.filter(is_local=True).exists()


@pytest.mark.django_db
def test_create_exchange_rate(currency_factory, exchange_rate_factory):
    # Create a local currency to satisfy the constraint
    local_currency = currency_factory(is_local=True)
    
    # Create a foreign currency
    foreign_currency = currency_factory(is_local=False)
    
    # Create an exchange rate for the foreign currency
    exchange_rate = exchange_rate_factory(currency=foreign_currency, rate=1.25)
    
    assert exchange_rate.currency == foreign_currency
    assert exchange_rate.rate == 1.25

@pytest.mark.django_db
def test_prevent_negative_exchange_rate(currency_factory, user):
    local_currency = currency_factory(is_local=True)
    currency = currency_factory(is_local=False, created_by=user)
    exchange_rate = ExchangeRate(currency=currency, rate=-5.00, created_by=user)
    with pytest.raises(ValidationError):
        exchange_rate.full_clean()

@pytest.mark.django_db
def test_prevent_zero_exchange_rate(currency_factory, user):
    local_currency = currency_factory(is_local=True)
    currency = currency_factory(is_local=False, created_by=user)
    exchange_rate = ExchangeRate(currency=currency, rate=0.00, created_by=user)
    with pytest.raises(ValidationError):
        exchange_rate.full_clean()

@pytest.mark.django_db
def test_local_currency_cannot_have_exchange_rate(currency_factory, user):
    local_currency = currency_factory(is_local=True, created_by=user)
    exchange_rate = ExchangeRate(currency=local_currency, rate=1.00, created_by=user)
    with pytest.raises(ValidationError):
        exchange_rate.full_clean() 

@pytest.mark.django_db
def test_exchange_rate_string_representation(currency_factory, exchange_rate_factory):
    # Create a local currency to satisfy the constraint
    local_currency = currency_factory(is_local=True)
    
    # Create an exchange rate
    exchange_rate = exchange_rate_factory(rate=1.5)
    
    # Expected string representation
    expected_str = f"Exchange rate for {exchange_rate.currency.code} on {exchange_rate.created_at:%B %d, %Y at %I:%M %p}"
    assert str(exchange_rate) == expected_str