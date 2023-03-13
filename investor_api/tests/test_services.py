from django.test import TestCase
from investor_api.models import CashFlow, Loan
from investor_api.services import (
    calculate_investment_date,
    calculate_invested_amount,
    calculate_expected_interest_amount,
    calculate_expected_irr,
    calculate_realized_irr,
    calculate_is_closed,
)
from datetime import datetime, timedelta
from pyxirr import xirr


class UtilsTestCase(TestCase):
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

        self.cf1 = CashFlow.objects.create(
            reference_date="2022-02-01",
            type="Funding",
            amount=-500,
            loan_identifier=self.loan,
        )
        self.cf2 = CashFlow.objects.create(
            reference_date="2022-03-01",
            type="Repayment",
            amount=250,
            loan_identifier=self.loan,
        )

    def test_calculate_investment_date(self):
        calculate_investment_date(self.loan)
        self.assertEqual(
            self.loan.investment_date,
            datetime.strptime(self.cf1.reference_date, "%Y-%m-%d").date(),
        )

    def test_calculate_invested_amount(self):
        calculate_invested_amount(self.loan)
        self.assertEqual(self.loan.invested_amount, abs(self.cf1.amount))

    def test_calculate_expected_interest_amount(self):
        calculate_invested_amount(self.loan)
        calculate_expected_interest_amount(self.loan)
        expected_interest = float(self.loan.total_expected_interest_amount) * (
            float(self.loan.invested_amount) / float(self.loan.total_amount)
        )
        self.assertEqual(self.loan.expected_interest_amount, expected_interest)

    def test_calculate_expected_irr(self):
        calculate_invested_amount(self.loan)
        calculate_expected_interest_amount(self.loan)
        calculate_expected_irr(self.loan)
        expected_irr = [
            (self.cf1.reference_date, self.cf1.amount),
            (
                self.loan.maturity_date,
                self.loan.invested_amount + self.loan.expected_interest_amount,
            ),
        ]
        self.assertAlmostEqual(self.loan.expected_irr, xirr(expected_irr), places=7)

    def test_calculate_realized_irr(self):
        self.loan.is_closed = True
        self.loan.save()

        calculate_realized_irr(self.loan)

        realized_irr = [
            (self.cf1.reference_date, self.cf1.amount),
            (self.cf2.reference_date, self.cf2.amount),
        ]
        self.assertAlmostEqual(self.loan.realized_irr, xirr(realized_irr), places=7)

    def test_calculate_is_closed(self):
        self.loan.investment_date = datetime.now().date() - timedelta(days=7)
        self.loan.invested_amount = 400
        self.loan.expected_interest_amount = 40
        self.loan.save()

        calculate_is_closed(loan=self.loan)

        self.assertEqual(self.loan.is_closed, False)

        self.cf3 = CashFlow.objects.create(
            reference_date="2023-02-01",
            type="Repayment",
            amount=560,
            loan_identifier=self.loan,
        )

        calculate_is_closed(loan=self.loan)

        self.assertEqual(self.loan.is_closed, True)
        self.assertAlmostEqual(self.loan.realized_irr, 1.1211098911638433, places=7)
