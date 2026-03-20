from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from stock.models import Stock, AccountCurrency, AccountStock
from stock.forms import BuySellForm, SellForm

def stock_list(request):
    stocks = Stock.objects.all()
    context = {
        'stocks': stocks,
    }
    return render(request, 'stocks.html', context)


@login_required
def stock_detail(request, pk, action='buy'):
    stock = get_object_or_404(Stock, pk=pk)
    
    if action == 'sell':
        form = SellForm()
        sell_mode = True
    else:
        form = BuySellForm(initial={'price': stock.get_random_price()})
        sell_mode = False
    
    context = {
        'stock': stock,
        'form': form,
        'sell_mode': sell_mode
    }
    return render(request, 'stock.html', context)

@login_required
def stock_buy(request, pk):
    if request.method != "POST":
        return redirect('stock:detail', pk=pk)

    stock = get_object_or_404(Stock, pk=pk)
    form = BuySellForm(request.POST)

    if form.is_valid():
        amount = form.cleaned_data['amount']
        price = form.cleaned_data['price']
        buy_cost = price * amount

        acc_stock, created = AccountStock.objects.get_or_create(
            account=request.user.account, 
            stock=stock,
            defaults={'average_buy_cost': 0, 'amount': 0}
        )
        
        current_cost = acc_stock.average_buy_cost * acc_stock.amount
        total_cost = current_cost + buy_cost
        total_amount = acc_stock.amount + amount
        
        acc_stock.amount = total_amount
        acc_stock.average_buy_cost = total_cost / total_amount

        acc_currency, created = AccountCurrency.objects.get_or_create(
            account=request.user.account, 
            currency=stock.currency,
            defaults={'amount': 0}
        )

        if acc_currency.amount < buy_cost:
            form.add_error(None, f'Не хватает достаточного средств в валюте {stock.currency.sign}')
        else:
            acc_currency.amount = acc_currency.amount - buy_cost
            acc_stock.save()
            acc_currency.save()
            cache.delete(f'currencies_{request.user.username}')
            cache.delete(f'stocks_{request.user.username}')
            return redirect('stock:list')

    context = {
        'stock': get_object_or_404(Stock, pk=pk),
        'form': form
    }
    return render(request, 'stock.html', context)


@login_required
def account(request):
    currencies = cache.get(f'currencies_{request.user.username}')
    stocks = cache.get(f'stocks_{request.user.username}')

    if currencies is None:
        currencies = [
            {
                'amount': acc_currency.amount,
                'sign': acc_currency.currency.sign
            } for acc_currency in
            request.user.account.accountcurrency_set.select_related('currency')
        ]
        cache.set(f'currencies_{request.user.username}', currencies, 300)

    if stocks is None:
        stocks = [
            {
                'ticker': acc_stock.stock.ticker,
                'amount': acc_stock.amount,
                'avg': acc_stock.average_buy_cost
            } for acc_stock in
            request.user.account.accountstock_set.select_related('stock').all()
        ]
        cache.set(f'stocks_{request.user.username}', stocks, 300)

    context = {
        'currencies': currencies,
        'stocks': stocks
    }

    return render(request, 'account.html', context=context)

@login_required
def stock_sell(request, pk):
    if request.method != "POST":
        return redirect('stock:list')
    
    stock = get_object_or_404(Stock, pk=pk)
    form = SellForm(request.POST)
    
    if form.is_valid():
        amount = form.cleaned_data['amount']
        current_price = stock.get_random_price()
        sell_value = current_price * amount
        acc_stock = AccountStock.objects.filter(
            account=request.user.account, 
            stock=stock
        ).first()
        
        if not acc_stock or acc_stock.amount < amount:
            return render(request, 'stock.html', {
                'stock': stock,
                'form': BuySellForm(initial={'price': current_price}),
                'sell_mode': True,
                'error': f'У вас нет {amount} акций {stock.ticker}. У вас есть {acc_stock.amount if acc_stock else 0} шт.'
            })
        acc_stock.amount -= amount
        if acc_stock.amount == 0:
            acc_stock.delete()
        else:
            acc_stock.save()
        acc_currency, created = AccountCurrency.objects.get_or_create(
            account=request.user.account,
            currency=stock.currency,
            defaults={'amount': 0}
        )
        acc_currency.amount += sell_value
        acc_currency.save()
        cache.delete(f'currencies_{request.user.username}')
        cache.delete(f'stocks_{request.user.username}')
        
        return redirect('stock:account')
    
    return redirect('stock:list')