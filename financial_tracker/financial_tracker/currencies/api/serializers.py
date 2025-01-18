from rest_framework import serializers
from ..models import Currency, ExchangeRate

class CurrencySerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    modified_by = serializers.ReadOnlyField(source='modified_by.username')
    def validate(self, data):
        if data.get("is_local", False):
            if Currency.objects.exclude(pk=self.instance.pk if self.instance else None).filter(is_local=True).exists():
                raise serializers.ValidationError("Only one local currency can exist.")
        elif not Currency.objects.filter(is_local=True).exists():
            raise serializers.ValidationError("Cannot set this currency as foreign; no local currency exists.")
        return data
    
    class Meta:
        model = Currency
        fields = ['code', 'description', 'is_local','created_by', 'created_at', 'modified_by', 'modified_at']

class ExchangeRateSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    modified_by = serializers.ReadOnlyField(source='modified_by.username')
    currency_description = serializers.CharField(source='currency.description', read_only=True)
    currency_is_local = serializers.CharField(source='currency.is_local', read_only=True)
    
    def validate(self, data):
        # Ensure the currency is not local
        if data['currency'].is_local:
            raise serializers.ValidationError("Cannot assign exchange rates to the local currency.")
        return data

    class Meta:
        model = ExchangeRate
        fields = ['id', 'currency', 'currency_description', 'currency_is_local', 'rate', 'created_by', 'created_at', 'modified_by', 'modified_at']