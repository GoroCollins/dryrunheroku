import factory
from ..models import EarnedIncome, PortfolioIncome, PassiveIncome
from financial_tracker.currencies.tests.factories import CurrencyFactory
from decimal import Decimal
from django.conf import settings

User = settings.AUTH_USER_MODEL

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True  # Prevents unnecessary saves

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    name = factory.Faker("name")

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)
        # Explicit save if modifications were made
        self.save()

class BaseIncomeFactory(factory.django.DjangoModelFactory):
    """
    This factory serves as a base for concrete income models (EarnedIncome, PortfolioIncome, PassiveIncome).
    You cannot instantiate BaseIncome directly because it is abstract.
    """
    income_name = factory.Faker("company")
    currency = factory.SubFactory(CurrencyFactory)
    amount = factory.Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    notes = factory.Faker("text")
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:
        abstract = True  # Mark this as abstract


class EarnedIncomeFactory(BaseIncomeFactory):
    class Meta:
        model = EarnedIncome


class PortfolioIncomeFactory(BaseIncomeFactory):
    class Meta:
        model = PortfolioIncome


class PassiveIncomeFactory(BaseIncomeFactory):
    class Meta:
        model = PassiveIncome
