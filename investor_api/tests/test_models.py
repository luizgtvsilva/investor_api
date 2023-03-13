from django.test import TestCase
from django.core.cache import cache
from investor_api.models import CustomUser, Loan, CashFlow


class CustomUserModelTests(TestCase):
    def test_user_creation(self):
        user = CustomUser.objects.create(username="testuser")
        self.assertTrue(isinstance(user, CustomUser))
        self.assertFalse(user.is_investor)
        self.assertFalse(user.is_analyst)


class LoanModelTests(TestCase):
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

    def test_loan_creation(self):
        self.assertTrue(isinstance(self.loan, Loan))
        self.assertEqual(self.loan.identifier, "loan1")
        self.assertEqual(self.loan.issue_date, "2022-01-01")
        self.assertEqual(self.loan.total_amount, 1000)
        self.assertEqual(self.loan.rating, 5)
        self.assertEqual(self.loan.maturity_date, "2023-01-01")
        self.assertEqual(self.loan.total_expected_interest_amount, 100)
        self.assertIsNone(self.loan.investment_date)
        self.assertIsNone(self.loan.invested_amount)
        self.assertIsNone(self.loan.expected_interest_amount)
        self.assertFalse(self.loan.is_closed)
        self.assertIsNone(self.loan.expected_irr)
        self.assertIsNone(self.loan.realized_irr)

    def test_loan_cache_invalidation(self):

        self.assertEqual(cache.get("foo"), None)

        Loan.objects.create(
            identifier="loan2",
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

        self.assertEqual(cache.get("foo"), None)


class CashFlowModelTests(TestCase):
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
        self.cash_flow = CashFlow.objects.create(
            reference_date="2022-02-01",
            type="Funding",
            amount=500,
            loan_identifier=self.loan,
        )

    def test_cash_flow_creation(self):
        self.assertTrue(isinstance(self.cash_flow, CashFlow))
        self.assertEqual(self.cash_flow.reference_date, "2022-02-01")
        self.assertEqual(self.cash_flow.type, "Funding")
        self.assertEqual(self.cash_flow.amount, 500)
        self.assertEqual(self.cash_flow.loan_identifier, self.loan)

    def test_cash_flow_cache_invalidation(self):

        self.assertEqual(cache.get("foo"), None)

        CashFlow.objects.create(
            reference_date="2022-03-01",
            type="Repayment",
            amount=250,
            loan_identifier=self.loan,
        )

        self.assertEqual(cache.get("foo"), None)
