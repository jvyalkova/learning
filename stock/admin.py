from django.contrib import admin
from stock.models import (Stock, Currency, Account, 
    AccountCurrency, AccountStock)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "description", "logo")


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "ticker", "sign")


# Inline классы для отображения в Account
class AccountCurrencyInline(admin.TabularInline):
    model = AccountCurrency


class AccountStockInline(admin.TabularInline):
    model = AccountStock


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [AccountCurrencyInline, AccountStockInline]


@admin.register(AccountCurrency)
class AccountCurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountStock)
class AccountStockAdmin(admin.ModelAdmin):
    pass