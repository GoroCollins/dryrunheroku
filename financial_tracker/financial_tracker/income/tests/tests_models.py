import pytest
from ..models import EarnedIncome
from .factories import EarnedIncomeFactory
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestBaseIncome:
    def test_amount_cannot_be_negative(self):
        earned_income = EarnedIncomeFactory(amount=-100)
        with pytest.raises(ValidationError) as excinfo:
            earned_income.full_clean()
        assert "Amount must be a non-negative value." in str(excinfo.value)

    def test_currency_is_required(self):
        earned_income = EarnedIncomeFactory(currency=None)
        with pytest.raises(ValidationError) as excinfo:
            earned_income.full_clean()
        assert "A valid currency must be provided." in str(excinfo.value)

    def test_amount_lcy_calculation(self, mocker):
        mocker.patch(
            "currencies.models.ExchangeRate.objects.get",
            return_value=mocker.Mock(rate=2.0)
        )
        earned_income = EarnedIncomeFactory(amount=100)
        earned_income.save()
        assert earned_income.amount_lcy == 200
@pytest.mark.django_db
class TestEarnedIncome:
    def test_verbose_name(self):
        income = EarnedIncomeFactory()
        assert str(income._meta.verbose_name) == "Earned Income"

@pytest.mark.django_db
class TestPortfolioIncome:
    def test_verbose_name(self):
        income = PortfolioIncomeFactory()
        assert str(income._meta.verbose_name) == "Portfolio Income"

class BaseIncomeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.user = User.objects.create(username="testuser")

        # Create a currency and exchange rate
        cls.currency = Currency.objects.create(code="USD", name="US Dollar")
        cls.exchange_rate = ExchangeRate.objects.create(currency=cls.currency, rate=100.00)  # Assume 1 USD = 100 LCY

    def test_valid_income_creation(self):
        # Create a valid EarnedIncome instance
        income = EarnedIncome.objects.create(
            income_name="Salary",
            currency=self.currency,
            amount=500,
            created_by=self.user
        )
        self.assertEqual(income.amount_lcy, 50000.00)  # 500 * 100

    def test_negative_amount_validation(self):
        with self.assertRaises(ValidationError):
            income = EarnedIncome(
                income_name="Invalid Income",
                currency=self.currency,
                amount=-100,
                created_by=self.user
            )
            income.full_clean()  # Validate before saving

    def test_missing_currency_validation(self):
        with self.assertRaises(ValidationError):
            income = EarnedIncome(
                income_name="No Currency Income",
                amount=500,
                created_by=self.user
            )
            income.full_clean()

    def test_missing_exchange_rate(self):
        # Create a currency without an exchange rate
        new_currency = Currency.objects.create(code="EUR", name="Euro")
        with self.assertRaises(ValidationError):
            income = EarnedIncome(
                income_name="No Exchange Rate",
                currency=new_currency,
                amount=500,
                created_by=self.user
            )
            income.full_clean()

    def test_amount_constraint(self):
        # Test that CheckConstraint prevents negative amounts
        with self.assertRaises(ValidationError):
            income = EarnedIncome(
                income_name="Negative Amount",
                currency=self.currency,
                amount=-500,
                created_by=self.user
            )
            income.full_clean()

    def test_amount_lcy_constraint(self):
        # Test that CheckConstraint prevents negative amount_lcy
        with self.assertRaises(ValidationError):
            income = EarnedIncome(
                income_name="Negative LCY",
                currency=self.currency,
                amount=500,
                created_by=self.user
            )
            income.amount_lcy = -100
            income.full_clean()
class ConcreteIncomeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.currency = Currency.objects.create(code="USD", name="US Dollar")
        cls.exchange_rate = ExchangeRate.objects.create(currency=cls.currency, rate=100.00)

    def test_earned_income_creation(self):
        income = EarnedIncome.objects.create(
            income_name="Freelance Work",
            currency=self.currency,
            amount=200,
            created_by=self.user
        )
        self.assertEqual(income.amount_lcy, 20000.00)
        self.assertEqual(income._meta.verbose_name, "Earned Income")
        self.assertEqual(income._meta.verbose_name_plural, "Earned Income")

    def test_portfolio_income_creation(self):
        income = PortfolioIncome.objects.create(
            income_name="Stock Dividends",
            currency=self.currency,
            amount=300,
            created_by=self.user
        )
        self.assertEqual(income.amount_lcy, 30000.00)
        self.assertEqual(income._meta.verbose_name, "Portfolio Income")
        self.assertEqual(income._meta.verbose_name_plural, "Portfolio Income")

    def test_passive_income_creation(self):
        income = PassiveIncome.objects.create(
            income_name="Rental Income",
            currency=self.currency,
            amount=400,
            created_by=self.user
        )
        self.assertEqual(income.amount_lcy, 40000.00)
        self.assertEqual(income._meta.verbose_name, "Passive Income")
        self.assertEqual(income._meta.verbose_name_plural, "Passive Income")
import pytest
from ..models import EarnedIncome, PortfolioIncome, PassiveIncome
from .factories import EarnedIncomeFactory, PortfolioIncomeFactory, PassiveIncomeFactory

@pytest.mark.django_db
@pytest.mark.parametrize("factory,model", [
    (EarnedIncomeFactory, EarnedIncome),
    (PortfolioIncomeFactory, PortfolioIncome),
    (PassiveIncomeFactory, PassiveIncome),
])
class TestIncomeModels:
    def test_amount_cannot_be_negative(self, factory, model):
        instance = factory(amount=-100)
        with pytest.raises(ValidationError):
            instance.full_clean()

    def test_amount_lcy_calculation(self, factory, model, mocker):
        mocker.patch(
            "currencies.models.ExchangeRate.objects.get",
            return_value=mocker.Mock(rate=1.5)
        )
        instance = factory(amount=100)
        instance.save()
        assert instance.amount_lcy == 150
