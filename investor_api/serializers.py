from rest_framework import serializers
from .models import Loan, CashFlow, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'is_investor', 'is_analyst')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_investor=validated_data['is_investor'],
            is_analyst=validated_data['is_analyst']
        )
        return user


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
