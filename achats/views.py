from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import FactureAchat, Produit
from .models import Demande, BonReception
from .facture_achat_pdf import generer_facture_achat_pdf
from .demande_pdf import generer_demande_pdf
from .br_pdf import generer_br_pdf
from .models import Fournisseur
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Produit


# ===============================
# INFO FOURNISSEUR (AJAX)
# ===============================


def fournisseur_info(request, fournisseur_id):

    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)

    return JsonResponse({
        "mf": fournisseur.matricule_fiscal or "",
        "adresse": fournisseur.adresse or "",
        "telephone": fournisseur.telephone or "",
        "email": fournisseur.email or "",
    })

# ===============================
# PDF BON RECEPTION
# ===============================
def br_pdf(request, id):

    br = get_object_or_404(BonReception, id=id)

    return generer_br_pdf(br)


# ===============================
# PDF FACTURE ACHAT
# ===============================
def facture_achat_pdf(request, facture_id):

    facture = get_object_or_404(FactureAchat, id=facture_id)

    return generer_facture_achat_pdf(facture)


# ===============================
# PDF DEMANDE PRIX
# ===============================
def demande_pdf(request, id):

    demande = get_object_or_404(Demande, id=id)

    return generer_demande_pdf(demande)


# ===============================
# INFO PRODUIT (AJAX)
# ===============================


def produit_info(request, produit_id):

    produit = get_object_or_404(Produit, id=produit_id)

    data = {
        "p_achat": float(produit.p_achat),
        "taux_tva": float(produit.taux_tva),
    }

    return JsonResponse(data)

from django.shortcuts import get_object_or_404
from .models import AvoirFournisseur
from .avoir_fournisseur_pdf import generer_avoir_fournisseur_pdf


def avoir_fournisseur_pdf(request, pk):

    avoir = get_object_or_404(AvoirFournisseur, pk=pk)

    return generer_avoir_fournisseur_pdf(avoir)