
from django.urls import path
from .views import facture_pdf, facture_xml, envoyer_facture
from .views import produit_info
from . import views

urlpatterns = [
    path("facture/<int:facture_id>/pdf/", facture_pdf, name="facture_pdf"),
    path("facture/<int:facture_id>/xml/", facture_xml, name="facture_xml"),
    path("facture/<int:facture_id>/envoyer/", envoyer_facture, name="envoyer_facture"),
    path("produit-info/<int:produit_id>/", views.produit_info, name="produit_info"),

     path(
     "client-info/<int:client_id>/",
     views.client_info,
     name="client_info"
     ),


    path("client-info/<int:client_id>/", views.client_info, name="client_info"),
    path("facture/<int:facture_id>/xml/", views.facture_xml, name="facture_xml"),
    path("devis/<int:id>/pdf/", views.devis_pdf, name="devis_pdf"),
    path("bl/<int:id>/pdf/", views.bl_pdf, name="bl_pdf"),
]
