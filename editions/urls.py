from django.urls import path
from . import views
from .views import facturation_globale,liste_bons_pdf,liste_factures_pdf,liste_factures_impression,liste_factachats_impression
from .views import liste_factachats_pdf



urlpatterns = [
    path('facturation-globale/', facturation_globale, name='facturation_globale'),
    path('dashboard-admin/', views.dashboard_admin, name='dashboard_admin'),  # le menu ERP
    path('bons/impression/', views.liste_bons_impression, name='liste_bons_impression'),
    path('liste_bons_pdf/', views.liste_bons_pdf, name='liste_bons_pdf'),
    path('liste_factures_impression/', views.liste_factures_impression, name='liste_factures_impression'),
    path('liste_factures_pdf/', views.liste_factures_pdf, name='liste_factures_pdf'),
    path('liste_factachats_impression/', views.liste_factachats_impression, name='liste_factachats_impression'),
    path('liste_factachats_pdf/', views.liste_factachats_pdf, name='liste_factachats_pdf'),
]