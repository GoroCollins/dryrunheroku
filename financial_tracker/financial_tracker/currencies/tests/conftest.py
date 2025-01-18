import pytest
from .factories import CurrencyFactory, ExchangeRateFactory, UserFactory

@pytest.fixture
def user():
    """
    Provides a single user instance for use in tests.
    """
    return UserFactory()

@pytest.fixture
def currency_factory():
    """
    Provides the CurrencyFactory class for generating multiple currency instances.
    """
    return CurrencyFactory

@pytest.fixture
def exchange_rate_factory():
    """
    Provides the ExchangeRateFactory class for generating exchange rate instances.
    """
    return ExchangeRateFactory
