from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from .models import Facture, Produit
from clients.models import Client
from .pdf import generer_facture_pdf
from .email import envoyer_facture_email
from .xml_generator import generer_facture_xml
from django.shortcuts import get_object_or_404
from .devis_pdf import generer_devis_pdf
from .models import Devis,BonLivraison
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404
from .models import BonLivraison
from .bl_pdf import generer_bl_pdf


def client_info(request, client_id):

    client = get_object_or_404(Client, id=client_id)

    return JsonResponse({
        "mf": client.matricule_fiscal or "",
        "adresse": client.adresse or "",
        "telephone": client.telephone or "",
        "email": client.email or "",
    })

def bl_pdf(request, id):

    bl = get_object_or_404(BonLivraison, id=id)

    return generer_bl_pdf(bl)


def facture_xml(request, facture_id):


    facture = get_object_or_404(Facture, id=facture_id)

    return generer_facture_xml(facture)


def facture_pdf(request, facture_id):

    facture = Facture.objects.get(id=facture_id)

    return generer_facture_pdf(facture)



def envoyer_facture(request, facture_id):

    facture = Facture.objects.get(id=facture_id)

    messages.success(request, f"Facture {facture.numero} envoyée (simulation).")

    return redirect("/admin/ventes/facture/")



def produit_info(request, produit_id):

    produit = Produit.objects.get(id=produit_id)

    return JsonResponse({
        "prix_ht": float(produit.prix_ht),
        "taux_tva": float(produit.taux_tva),
    })



def devis_pdf(request, id):

    devis = get_object_or_404(Devis, id=id)

    return generer_devis_pdf(devis)