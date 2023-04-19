from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from apps.home.models import Budget, Transaction

# budget/forms.py

class BudgetForm(forms.ModelForm):
    category = forms.CharField(
        label='Budget item',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Budget item'})
    )
    budget_amount = forms.DecimalField(
        label='Cost',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost'})
    )

    class Meta:
        model = Budget
        fields = ['category', 'budget_amount']



class TransactionForm(forms.ModelForm):
    TRANSACTION_TYPE_CHOICES = [
        ('', 'Select Transaction Type'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    INCOME_CATEGORY_CHOICES = [
        ('', 'Select Category'),
        ('salary', 'Salary'),
        ('gift', 'Gift'),
        ('investments', 'Investments'),
        ('other', 'Other'),
    ]

    EXPENSE_CATEGORY_CHOICES = [
        ('', 'Select Category'),
        ('Rent', 'Rent'),
        ('Electricity', 'Electricity'),
        ('Groceries', 'Groceries'),
        ('Entertainment', 'Entertainment'),
        ('Other', 'Other'),
    ]

    transaction_date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    description = forms.CharField(
        label='Description',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    transaction_type = forms.ChoiceField(
        label='Transaction Type',
        choices=TRANSACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ChoiceField(
        label='Category',
        choices=EXPENSE_CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        label='Amount',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    class Meta:
        model = Transaction
        fields = ['transaction_date', 'description', 'transaction_type', 'category', 'amount']

    def __init__(self, *args, **kwargs):
        transaction_type = kwargs.pop('transaction_type', 'expense')
        super().__init__(*args, **kwargs)
        self.update_category_choices(transaction_type)

    def update_category_choices(self, transaction_type):
        if transaction_type == 'income':
            self.fields['category'].choices = self.INCOME_CATEGORY_CHOICES
        else:
            self.fields['category'].choices = self.EXPENSE_CATEGORY_CHOICES








