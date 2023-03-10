import numpy_financial as npf


def calculate_investment_date(loan):
    funding_cashflow = loan.cashflow_set.get(type='funding')
    loan.investment_date = funding_cashflow.reference_date.date()
    loan.save()


def calculate_invested_amount(loan):
    funding_cashflow = loan.cashflow_set.get(type='funding')
    loan.invested_amount = funding_cashflow.amount
    loan.save()


def calculate_expected_interest_amount(loan):
    total_expected_interest = loan.total_expected_interest_amount
    total_amount = loan.total_amount
    invested_amount = loan.invested_amount
    loan.expected_interest_amount = total_expected_interest * (invested_amount / total_amount)
    loan.save()


def calculate_is_closed(loan):
    total_repaid_amount = loan.total_repaid_amount
    expected_amount = loan.invested_amount + loan.expected_interest_amount
    if total_repaid_amount >= expected_amount:
        loan.is_closed = True
    else:
        loan.is_closed = False
    loan.save()


def calculate_expected_irr(loan):
    funding_cashflow = loan.cashflow_set.get(type='funding')
    maturity_date = loan.maturity_date
    invested_amount = loan.invested_amount
    expected_interest_amount = loan.expected_interest_amount
    cash_flows = [
        (funding_cashflow.reference_date.date(), -funding_cashflow.amount),
        (maturity_date, invested_amount + expected_interest_amount)
    ]
    loan.expected_irr = npf.xirr(cash_flows)
    loan.save()


def calculate_realized_irr(loan):
    funding_cashflow = loan.cashflow_set.get(type='funding')
    repayment_cashflows = loan.cashflow_set.filter(type='repayment')
    cash_flows = [
        (funding_cashflow.reference_date.date(), -funding_cashflow.amount)
    ]
    for repayment_cashflow in repayment_cashflows:
        cash_flows.append((repayment_cashflow.reference_date.date(),
                           repayment_cashflow.amount))
    loan.realized_irr = npf.xirr(cash_flows)
    loan.save()
