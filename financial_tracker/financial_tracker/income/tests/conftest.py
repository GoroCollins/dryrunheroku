import pytest 
from .factories import CurrencyFactory, UserFactory, EarnedIncomeFactory, PortfolioIncomeFactory, PassiveIncomeFactory

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
def earned_income_factory():
    """
    Provides the EarnedIncomeFactory class for generating multiple earned income instances.
    """
    return EarnedIncomeFactory

@pytest.fixture
def portfolio_income_factory():
    """
    Provides the PortfolioIncomeFactory class for generating multiple portfolio income instances.
    """
    return PortfolioIncomeFactory

@pytest.fixture
def passive_income_factory():
    """
    Provides the PassiveIncomeFactory class for generating multiple passive income instances.
    """
    return PassiveIncomeFactory