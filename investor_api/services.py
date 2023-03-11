from scipy.optimize import root
from investor_api.models import CashFlow
from django.db.models import Sum
import datetime


def calculate_investment_date(loan):
    funding_cashflow = CashFlow.objects.filter(loan_identifier=loan.identifier,
                                               type='Funding').last()
    if funding_cashflow:
        loan.investment_date = funding_cashflow.reference_date
        loan.save()


def calculate_invested_amount(loan):
    funding_cashflow = CashFlow.objects.filter(loan_identifier=loan.identifier,
                                               type='Funding').last()

    if funding_cashflow:
        loan.invested_amount = abs(funding_cashflow.amount)
        loan.save()


def calculate_expected_interest_amount(loan):
    total_expected_interest = loan.total_expected_interest_amount
    total_amount = loan.total_amount
    invested_amount = loan.invested_amount
    loan.expected_interest_amount = float(total_expected_interest) * (float(invested_amount) / float(total_amount))
    loan.save()


def calculate_is_closed(loan):
    total_repayment = CashFlow.objects.filter(loan_identifier=loan.identifier,
                                              type='Repayment').aggregate(
                                                total=Sum('amount')
                                                )['total']

    if total_repayment:
        expected_amount = loan.invested_amount + loan.expected_interest_amount
        if total_repayment >= expected_amount:
            loan.is_closed = True
        else:
            loan.is_closed = False
        loan.save()


def npv(rate, cash_flows):
    total = 0
    for i, cash_flow in enumerate(cash_flows):
        if isinstance(cash_flow[0], str):
            cash_flow_date = datetime.datetime.strptime(cash_flow[0], '%Y-%m-%d').date()
        else:
            cash_flow_date = cash_flow[0]
        total += cash_flow[1] / ((1 + rate) ** ((cash_flow_date - cash_flows[0][0]).days / 365.0))
    return total


def calculate_expected_irr(loan):
    funding_cashflow = CashFlow.objects.filter(loan_identifier=loan.identifier,
                                               type='Funding').last()
    maturity_date = loan.maturity_date
    invested_amount = loan.invested_amount
    expected_interest_amount = loan.expected_interest_amount
    cash_flows = [
        (funding_cashflow.reference_date, funding_cashflow.amount),
        (maturity_date, invested_amount + abs(expected_interest_amount))
    ]
    loan.expected_irr = root(lambda r: npv(r, cash_flows), 0.0).x[0]
    loan.save()


def calculate_realized_irr(loan):
    funding_cashflow = CashFlow.objects.filter(loan_identifier=loan.identifier,
                                               type='Funding').last()
    repayment_cashflows = CashFlow.objects.filter(loan_identifier=loan.identifier,
                                               type='Repayment')
    cash_flows = [
        (funding_cashflow.reference_date, - funding_cashflow.amount)
    ]
    for repayment_cashflow in repayment_cashflows:
        cash_flows.append((repayment_cashflow.reference_date,
                           repayment_cashflow.amount))
    loan.realized_irr = root(lambda r: npv(r, cash_flows), 0.0).x[0]
    loan.save()
