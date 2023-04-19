# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.PROTECT)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f'id={str(self.id)}'
    # add any additional user profile fields, such as a profile picture, if needed

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255)
    transaction_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, null=True)





class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)



