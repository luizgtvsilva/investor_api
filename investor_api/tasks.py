from celery import shared_task
from .models import Loan, CashFlow
import csv
from io import StringIO


@shared_task
def process_csv(loan_csv_content, cash_flow_csv_content):
    loan_csv = csv.DictReader(StringIO(loan_csv_content))
    cash_flow_csv = csv.DictReader(StringIO(cash_flow_csv_content))

    # Processa o arquivo csv de empréstimos
    for row in loan_csv:
        loan = Loan.objects.create(
            identifier=row['identifier'],
            issue_date=row['issue_date'],
            total_amount=row['total_amount'],
            rating=row['rating'],
            maturity_date=row['maturity_date'],
            total_expected_interest_amount=row['total_expected_interest_amount']
        )

    # Processa o arquivo csv de fluxo de caixa
    for row in cash_flow_csv:
        loan = Loan.objects.get(identifier=row['loan_identifier'])
        cash_flow = CashFlow.objects.create(
            loan_identifier=loan,
            reference_date=row['reference_date'],
            type=row['type'],
            amount=row['amount']
        )