from rest_framework import serializers
from ..models import EarnedIncome, PortfolioIncome, PassiveIncome

class BaseIncomeSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    modified_by = serializers.ReadOnlyField(source='modified_by.username')
    #currency_symbol = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id',  'income_name', 'currency', 'amount', 'notes', 'created_by', 'created_at', 'modified_by', 'modified_at', 
        ]

    # def get_currency_symbol(self, obj):
    #     # Return the human-readable form of the currency
    #     return obj.get_currency_display()

    def validate(self, data):
        # Validate non-negative amount and amount_lcy
        if data.get('amount') < 0:
            raise serializers.ValidationError("Amount must be non-negative.")
        return data
class EarnedIncomeSerializer(BaseIncomeSerializer):
    class Meta(BaseIncomeSerializer.Meta):
        model = EarnedIncome


class PortfolioIncomeSerializer(BaseIncomeSerializer):
    class Meta(BaseIncomeSerializer.Meta):
        model = PortfolioIncome


class PassiveIncomeSerializer(BaseIncomeSerializer):
    class Meta(BaseIncomeSerializer.Meta):
        model = PassiveIncome
#'url','currency_symbol'