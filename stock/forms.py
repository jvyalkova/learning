from django import forms

class BuySellForm(forms.Form):
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    amount = forms.IntegerField(min_value=1)

class SellForm(forms.Form):
    amount = forms.IntegerField(min_value=1)