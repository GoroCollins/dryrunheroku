import factory
from ..models import Currency, ExchangeRate
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
class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Faker("currency_code")
    description = factory.Faker("currency_name")
    is_local = False
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate

    currency = factory.SubFactory(CurrencyFactory)
    rate = factory.Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)
    
    
