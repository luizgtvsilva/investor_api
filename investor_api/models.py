from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Permission, Group


class CustomUser(AbstractUser):
    is_investor = models.BooleanField(default=False)
    is_analyst = models.BooleanField(default=False)
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_users',
        help_text='The permissions this user has',
        related_query_name='custom_user'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_users',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='custom_user'
    )

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


@receiver(post_save, sender=Loan)
@receiver(post_save, sender=CashFlow)
def invalidate_cache(sender, **kwargs):
    cache.clear()
