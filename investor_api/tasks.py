from celery import shared_task
from .models import Loan, CashFlow
import csv
from io import StringIO
from .services import (
    calculate_investment_date,
    calculate_invested_amount,
    calculate_expected_interest_amount,
    calculate_is_closed,
    calculate_expected_irr,
    calculate_realized_irr,)


@shared_task
def process_csv(loan_csv_content, cash_flow_csv_content):
    Loan.objects.all().delete()
    loan_csv = csv.DictReader(StringIO(loan_csv_content))
    cash_flow_csv = csv.DictReader(StringIO(cash_flow_csv_content))
    loans_created = []

    for row in loan_csv:
        loan = Loan.objects.create(
            identifier=row['identifier'],
            issue_date=row['issue_date'],
            total_amount=row['total_amount'],
            rating=row['rating'],
            maturity_date=row['maturity_date'],
            total_expected_interest_amount=row['total_expected_interest_amount']
        )
        loans_created.append(loan)

    for row in cash_flow_csv:
        loan = Loan.objects.get(identifier=row['loan_identifier'])
        cash_flow = CashFlow.objects.create(
            loan_identifier=loan,
            reference_date=row['reference_date'],
            type=row['type'],
            amount=row['amount']
        )

    for loan in loans_created:
        calculate_investment_date(loan)
        calculate_invested_amount(loan)
        calculate_expected_interest_amount(loan)
        calculate_is_closed(loan)
        calculate_expected_irr(loan)
        calculate_realized_irr(loan)