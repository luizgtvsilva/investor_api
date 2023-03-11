from rest_framework import serializers
from .models import Loan, CashFlow


class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlow
        fields = '__all__'


class LoanDetailSerializer(serializers.ModelSerializer):
    cash_flows = CashFlowSerializer(many=True)

    class Meta:
        model = Loan
        fields = ['identifier',
                  'issue_date',
                  'total_amount',
                  'rating',
                  'maturity_date',
                  'total_expected_interest_amount',
                  'investment_date',
                  'invested_amount',
                  'expected_interest_amount',
                  'is_closed',
                  'expected_irr',
                  'realized_irr',
                  'cash_flows']


class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


class CashFlowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlow
        fields = '__all__'

    def create(self, validated_data):
        loan_identifier = validated_data.pop('loan_identifier')
        loan = Loan.objects.get(identifier=loan_identifier.identifier)
        cash_flow = CashFlow.objects.create(loan_identifier=loan,
                                            **validated_data)
        return cash_flow
