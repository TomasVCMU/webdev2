# -*- encoding: utf-8 -*-

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.urls import reverse
import traceback
import json
import datetime
from django.db.models.functions import ExtractMonth
from django.shortcuts import render, redirect
from django.contrib import messages
# from datetime import datetime, date, timedelta
from django.db.models import Sum, Case, When, DecimalField
from django.shortcuts import render
from django.utils import timezone

from apps.home.forms import BudgetForm, TransactionForm
from apps.home.models import Budget, Transaction

from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@login_required(login_url="/login/")
def index(request):
    # Retrieve user's transactions
    transactions = Transaction.objects.filter(user=request.user)

    # Calculate total income and expenses
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate the total expenses for each category
    expense_categories = transactions.values('category').annotate(total=Sum('amount'))
    expense_categories = list(expense_categories)
    for category in expense_categories:
        category['total'] = float(category['total'])

    # Calculate monthly expense breakdown
    expenses = transactions.filter(transaction_type='expense')\
        .values('category')\
        .annotate(total_amount=Sum('amount'))
    data = [
        {'name': expense['category'], 'value': expense['total_amount']}
        for expense in expenses
    ]
    # Get the user's current monthly income
    # total_income = request.user.profile.monthly_income
    # Calculate balance
    balance = total_income - total_expenses

    # Retrieve user's total budget
    user_budgets = Budget.objects.filter(user=request.user)
    total_budget = user_budgets.aggregate(Sum('budget_amount'))['budget_amount__sum'] or 0
    
    current_year = datetime.datetime.now().year
    monthly_data = transactions.filter(transaction_date__year=current_year).annotate(
        month=ExtractMonth('transaction_date')
    ).values('month').annotate(
        income=Sum(
            Case(
                When(transaction_type='income', then='amount'),
                default=0,
                 output_field=DecimalField()
            )
        ),
        expenses=Sum(
            Case(
                When(transaction_type='expense', then='amount'),
                default=0,
                 output_field=DecimalField()
            )
        )
    )
    
    # Convert QuerySet to list of dictionaries
    monthly_data = list(monthly_data)
    
    # Expenses
    expense_categories_pie = transactions.filter(transaction_type='expense').values('category').annotate(total=Sum('amount'))
    expense_categories_pie = list(expense_categories_pie)
    
    expense_categories_data = {
    'labels': [category['category'] for category in expense_categories_pie],
    'values': [float(category['total']) for category in expense_categories_pie],}

    context = {
        'segment': 'index',
        'monthly_data_json': json.dumps(monthly_data, cls=DecimalEncoder),
        'current_year': current_year,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': abs(total_expenses),
        'balance': balance,
        'budget': total_budget,
        'expense_categories': expense_categories,
        'expense_categories_data': json.dumps(expense_categories_data)
    }
    print(json.dumps(monthly_data, cls=DecimalEncoder))
    # If the request is AJAX, return the JSON response
    if request.is_ajax():
        return JsonResponse({'data': data})

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))




def handle_budget(request, context):
    user = request.user
    budgets = Budget.objects.filter(user=user)
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = user
            budget.save()
            return redirect('budget')
    else:
        form = BudgetForm()

    context.update({'form': form, 'budgets': budgets})

    return render(request, 'home/budget.html', context)



def handle_transactions(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')
    if request.method == 'POST':
        return _extracted_from_handle_transactions_(request, user)
    else:
        form = TransactionForm()

    context = {
        'transactions': transactions,
        'form': form,
    }

    return render(request, 'home/transaction.html', context)


# TODO Rename this here and in `handle_transactions`
def _extracted_from_handle_transactions_(request, user):
    transaction_type = request.POST.get('transaction_type', 'expense')
    form = TransactionForm(request.POST, transaction_type=transaction_type)
    if not form.is_valid():
        #  html_template = loader.get_template('home/page-500.html')
        return HttpResponse(loader.get_template('home/page-500.html').render(context, request))
    transaction = form.save(commit=False)
    transaction.user = user
    transaction.save()
    return HttpResponseRedirect('/transactions/')  # Change this line






@login_required(login_url="/login/")
def pages(request):
    context = {}

    try:
        path_parts = request.path.strip('/').split('/')
        load_template = path_parts[-1] or path_parts[-2]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        context['segment'] = load_template

        # Check if the requested page is the budget page
        if load_template == 'budget':
            return handle_budget(request, context)
        elif load_template == 'transactions':
            return handle_transactions(request)
        else:
            html_template = loader.get_template(f'home/{load_template}')

        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        traceback.print_exc()
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@csrf_exempt
def monthly_expense_breakdown(request):
    if request.method == 'GET':
        # Calculate monthly expense breakdown
        expenses = Transaction.objects.filter(transaction_type='expense')\
                                      .values('category')\
                                      .annotate(total_amount=Sum('amount'))

        data = [
            {'name': expense['category'], 'value': expense['total_amount']}
            for expense in expenses
        ]
        print(data)
        return JsonResponse({'data': data})