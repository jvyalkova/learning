from django.urls import path
from stock.views import stock_list, stock_detail, stock_buy, stock_sell, account

app_name = 'stock'

urlpatterns = [
    path('list/', stock_list, name='list'),
    path('detail/<int:pk>/', stock_detail, name='detail'),
    path('detail/<int:pk>/sell/', stock_detail, {'action': 'sell'}, name='detail_sell'),
    path('buy/<int:pk>/', stock_buy, name='buy'),
    path('sell/<int:pk>/', stock_sell, name='sell'),
    path('account/', account, name='account'),
]