from django.test import TestCase
from investor_api.models import CustomUser, Loan, CashFlow
from investor_api.serializers import (
    CustomUserSerializer,
    CashFlowSerializer,
    LoanDetailSerializer,
    CashFlowCreateSerializer,
)


class CustomUserSerializerTestCase(TestCase):
    def test_create_user(self):
        data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "password",
            "is_investor": True,
            "is_analyst": False,
        }
        serializer = CustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.username, "user1")
        self.assertEqual(user.email, "user1@example.com")
        self.assertTrue(user.check_password("password"))
        self.assertTrue(user.is_investor)
        self.assertFalse(user.is_analyst)


class CashFlowSerializerTestCase(TestCase):
    def test_serialize_cash_flow(self):
        loan = Loan.objects.create(
            identifier="loan1",
            issue_date="2022-01-01",
            total_amount=1000,
            rating=5,
            maturity_date="2023-01-01",
            total_expected_interest_amount=100,
            investment_date=None,
            invested_amount=None,
            expected_interest_amount=None,
            is_closed=False,
            expected_irr=None,
            realized_irr=None,
        )
        cash_flow = CashFlow.objects.create(
            reference_date="2022-02-01",
            type="Funding",
            amount=500,
            loan_identifier=loan,
        )
        serializer = CashFlowSerializer(cash_flow)
        expected_data = {
            "id": cash_flow.id,
            "reference_date": "2022-02-01",
            "type": "Funding",
            "amount": 500,
            "loan_identifier": loan.identifier,
        }
        self.assertEqual(serializer.data, expected_data)


class LoanDetailSerializerTestCase(TestCase):
    def test_serialize_loan_detail(self):
        loan = Loan.objects.create(
            identifier="loan1",
            issue_date="2022-01-01",
            total_amount=1000,
            rating=5,
            maturity_date="2023-01-01",
            total_expected_interest_amount=100,
            investment_date=None,
            invested_amount=None,
            expected_interest_amount=None,
            is_closed=False,
            expected_irr=None,
            realized_irr=None,
        )
        cash_flow1 = CashFlow.objects.create(
            reference_date="2022-02-01",
            type="Funding",
            amount=500,
            loan_identifier=loan,
        )
        cash_flow2 = CashFlow.objects.create(
            reference_date="2022-03-01",
            type="Repayment",
            amount=250,
            loan_identifier=loan,
        )
        serializer = LoanDetailSerializer(loan)
        expected_data = {
            "identifier": "loan1",
            "issue_date": "2022-01-01",
            "total_amount": 1000,
            "rating": 5,
            "maturity_date": "2023-01-01",
            "total_expected_interest_amount": 100,
            "investment_date": None,
            "invested_amount": None,
            "expected_interest_amount": None,
            "is_closed": False,
            "expected_irr": None,
            "realized_irr": None,
            "cash_flows": [
                {
                    "id": cash_flow1.id,
                    "reference_date": "2022-02-01",
                    "type": "Funding",
                    "amount": 500,
                    "loan_identifier": "loan1",
                },
                {
                    "id": cash_flow2.id,
                    "reference_date": "2022-03-01",
                    "type": "Repayment",
                    "amount": 250,
                    "loan_identifier": "loan1",
                },
            ],
        }
        self.assertEqual(serializer.data, expected_data)


class CashFlowCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.loan = Loan.objects.create(
            identifier="loan1",
            issue_date="2022-01-01",
            total_amount=1000,
            rating=5,
            maturity_date="2023-01-01",
            total_expected_interest_amount=100,
            investment_date=None,
            invested_amount=None,
            expected_interest_amount=None,
            is_closed=False,
            expected_irr=None,
            realized_irr=None,
        )

    def test_create_cash_flow(self):
        data = {
            "reference_date": "2022-03-01",
            "type": "Repayment",
            "amount": 250,
            "loan_identifier": "loan1",
        }
        serializer = CashFlowCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        cash_flow = serializer.save()
        self.assertTrue(isinstance(cash_flow, CashFlow))
        self.assertEqual(cash_flow.reference_date.strftime("%Y-%m-%d"), "2022-03-01")
        self.assertEqual(cash_flow.type, "Repayment")
        self.assertEqual(cash_flow.amount, 250)
        self.assertEqual(cash_flow.loan_identifier, self.loan)
