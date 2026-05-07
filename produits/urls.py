from django.urls import path
from .views import liste_stock,stock_produit

urlpatterns = [
    path('stock/', liste_stock, name='liste_stock'),
    path("stock/<int:produit_id>/", stock_produit, name="stock_produit"),
]