from django.db import models


class Loan(models.Model):
    identifier = models.CharField(max_length=256, unique=True)
    issue_date = models.DateField()
    total_amount = models.FloatField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 10)])
    maturity_date = models.DateField()
    total_expected_interest_amount = models.FloatField()
    investment_date = models.DateField(null=True, blank=True)
    invested_amount = models.FloatField(null=True, blank=True)
    expected_interest_amount = models.FloatField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    expected_irr = models.FloatField(null=True, blank=True)
    realized_irr = models.FloatField(null=True, blank=True)
    

class CashFlow(models.Model):
    reference_date = models.DateField()
    type = models.CharField(choices=[
        ('Funding', 'Funding'),
        ('Repayment', 'Repayment'),
    ], max_length=20)
    amount = models.FloatField()
    loan_identifier = models.ForeignKey(Loan,
                                        on_delete=models.CASCADE,
                                        related_name='cash_flows',
                                        to_field='identifier',
                                        null=True, blank=True,
                                        default=None)
