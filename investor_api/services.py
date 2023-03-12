from pyxirr import xirr
from investor_api.models import CashFlow, Loan
from django.db.models import Sum


def calculate_investment_date(loan):
    funding_cashflow = CashFlow.objects.filter(
        loan_identifier=loan.identifier, type="Funding"
    ).last()
    if funding_cashflow:
        loan.investment_date = funding_cashflow.reference_date
        loan.save()


def calculate_invested_amount(loan):
    funding_cashflow = CashFlow.objects.filter(
        loan_identifier=loan.identifier, type="Funding"
    ).last()

    if funding_cashflow:
        loan.invested_amount = abs(funding_cashflow.amount)
        loan.save()


def calculate_expected_interest_amount(loan):
    total_expected_interest = loan.total_expected_interest_amount
    total_amount = loan.total_amount
    invested_amount = loan.invested_amount
    loan.expected_interest_amount = float(total_expected_interest) * (
        float(invested_amount) / float(total_amount)
    )
    loan.save()


def calculate_expected_irr(loan):
    cf = CashFlow.objects.filter(loan_identifier=loan.identifier, type="Funding").last()

    expected_irr = [
        (cf.reference_date, cf.amount),
        (loan.maturity_date, loan.invested_amount + loan.expected_interest_amount),
    ]

    loan.expected_irr = xirr(expected_irr)
    loan.save()


def calculate_realized_irr(loan):
    if loan.is_closed:
        cf = CashFlow.objects.filter(
            loan_identifier=loan.identifier, type="Funding"
        ).last()
        cf_repayments = CashFlow.objects.filter(
            loan_identifier=loan.identifier, type="Repayment"
        )

        realized_irr = [(cf.reference_date, cf.amount)]

        for repayment in cf_repayments:
            realized_irr.append((repayment.reference_date, repayment.amount))

        loan.realized_irr = xirr(realized_irr)
        loan.save()


def calculate_is_closed(loan=None, loan_identifier=None):
    if not loan:
        loan = Loan.objects.get(identifier=loan_identifier)

    total_repayment = CashFlow.objects.filter(
        loan_identifier=loan.identifier, type="Repayment"
    ).aggregate(total=Sum("amount"))["total"]

    if total_repayment:
        expected_amount = loan.invested_amount + loan.expected_interest_amount
        if total_repayment >= expected_amount:
            loan.is_closed = True
            loan.save()
            calculate_realized_irr(loan)
        else:
            loan.is_closed = False
            loan.save()
