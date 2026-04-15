from django.urls import path
from .views import fournisseur_info,releve_fournisseur, releve_fournisseur_pdf

urlpatterns = [
    path("fournisseur-info/<int:fournisseur_id>/", fournisseur_info, name="fournisseur_info"),
    path('releve-fournisseur/<int:fournisseur_id>/', releve_fournisseur, name='releve_fournisseur'),
    path('releve-fournisseur/<int:fournisseur_id>/pdf/', releve_fournisseur_pdf, name='releve_fournisseur_pdf'),
]