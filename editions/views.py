from django.shortcuts import render, redirect
from django.utils import timezone
from ventes.models import BonLivraison, Facture, Client
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def dashboard_admin(request):
    """
    Dashboard ERP admin
    """
    return render(request, "editions/admin_dashboard.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from ventes.models import BonLivraison, Facture, LigneBonLivraison, LigneFacture, Client

def generer_numero_facture():
    annee = now().year
    prefix = f"FAC-{annee}-"
    derniere = Facture.objects.filter(numero__startswith=prefix).order_by("numero").last()
    if derniere and derniere.numero:
        try:
            num = int(derniere.numero.split("-")[-1]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:05d}"

@staff_member_required
def facturation_globale(request):
    clients = Client.objects.all()
    bons = BonLivraison.objects.filter(facture__isnull=True).order_by("-date")
    
    # Filtre client / date
    client_id = request.GET.get("client")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    if client_id:
        bons = bons.filter(client_id=client_id)
    if date_debut:
        bons = bons.filter(date__gte=date_debut)
    if date_fin:
        bons = bons.filter(date__lte=date_fin)

    facture_creee = None

    if request.method == "POST":
        bons_ids = request.POST.getlist("bons_ids")
        if not bons_ids:
            messages.warning(request, "Aucun bon sélectionné !")
            return redirect('facturation_globale')

        bons_selectionnes = bons.filter(id__in=bons_ids)
        if not bons_selectionnes.exists():
            messages.warning(request, "Les bons sélectionnés ont déjà été facturés !")
            return redirect('facturation_globale')

        client = bons_selectionnes.first().client
        numero = generer_numero_facture()

        # Création de la facture
        facture_creee = Facture.objects.create(
            numero=numero,
            client=client,
            date=now(),
            statut='brouillon',
            mf_client=bons_selectionnes.first().mf_client,
            adresse_client=bons_selectionnes.first().adresse_client,
            telephone_client=bons_selectionnes.first().telephone_client,
            email_client=bons_selectionnes.first().email_client
        )

        # Copier toutes les lignes de bons sélectionnés
        total_ht = total_rem = base_tva = total_tva = total_ttc = 0
        for bon in bons_selectionnes:
            for ligne in bon.lignes.all():
                montant_ht = ligne.quantite * ligne.prix_ht
                remise = montant_ht * (ligne.taux_rem / 100)
                base = montant_ht - remise
                tva = base * (ligne.taux_tva / 100)
                ttc = base + tva

                # Créer LigneFacture
                LigneFacture.objects.create(
                    facture=facture_creee,
                    produit=ligne.produit,
                    quantite=ligne.quantite,
                    prix_ht=ligne.prix_ht,
                    taux_rem=ligne.taux_rem,
                    taux_tva=ligne.taux_tva
                )

                # Cumuler totaux
                total_ht += montant_ht
                total_rem += remise
                base_tva += base
                total_tva += tva
                total_ttc += ttc

        # Mettre à jour la facture avec les totaux
        facture_creee.total_ht = total_ht
        facture_creee.total_rem = total_rem
        facture_creee.base_tva = base_tva
        facture_creee.total_tva = total_tva
        facture_creee.total_ttc = total_ttc
        facture_creee.save()

        # Lier les bons à la facture
        bons_selectionnes.update(facture=facture_creee, statut='validee')

        messages.success(request, f"Facture {facture_creee.numero} créée avec succès !")
        return redirect('facturation_globale')

    return render(request, "editions/facturation_globale.html", {
        "clients": clients,
        "bons": bons,
        "facture_creee": facture_creee
    })
#-----------   Facturation des bons selectionner
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from ventes.models import BonLivraison, Facture

@staff_member_required
def facturer_bons(request):
    if request.method == "POST":
        # Récupérer les bons cochés
        bons_ids = request.POST.getlist("bons_ids")
        if not bons_ids:
            messages.warning(request, "Aucun bon sélectionné !")
            return redirect('facturation_globale')

        # Filtrer uniquement les bons non facturés
        bons = BonLivraison.objects.filter(id__in=bons_ids, facture__isnull=True)
        if not bons.exists():
            messages.warning(request, "Les bons sélectionnés ont déjà été facturés !")
            return redirect('facturation_globale')

        # On suppose que tous les bons sont du même client
        client = bons.first().client

        # Création de la facture
        facture = Facture.objects.create(
            client=client,
            date=now(),
            total_ht=sum(b.total_ht for b in bons),
            total_rem=sum(b.total_rem for b in bons),
            base_tva=sum(b.base_tva for b in bons),
            total_tva=sum(b.total_tva for b in bons),
            total_ttc=sum(b.total_ttc for b in bons),
            statut='brouillon',
            mf_client=bons.first().mf_client,
            adresse_client=bons.first().adresse_client,
            telephone_client=bons.first().telephone_client,
            email_client=bons.first().email_client,
        )

        # Lier les bons à la facture et marquer comme validée
        bons.update(facture=facture, statut='validee')

        messages.success(request, f"Facture {facture.numero or facture.id} créée avec succès !")
        return redirect('facturation_globale')

    return redirect('facturation_globale')




# ---------------- IMPORTS ----------------
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from ventes.models import BonLivraison
from fpdf import FPDF


# ---------------- QUERYSET ----------------
def get_bons_queryset(date_debut, date_fin):
    bons = BonLivraison.objects.all()

    if date_debut:
        bons = bons.filter(date__gte=date_debut)

    if date_fin:
        bons = bons.filter(date__lte=date_fin)

    return bons.order_by("date")


# ---------------- HTML ----------------
def liste_bons_impression(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    bons = get_bons_queryset(date_debut, date_fin)

    totaux = bons.aggregate(
        total_ht=Sum("total_ht"),
        total_rem=Sum("total_rem"),
        base_tva=Sum("base_tva"),
        total_tva=Sum("total_tva"),
        total_ttc=Sum("total_ttc"),
    )

    # éviter None
    for k in totaux:
        totaux[k] = totaux[k] or 0

    return render(request, "editions/liste_bons_impression.html", {
        "bons": bons,
        "totaux": totaux,
        "date_debut": date_debut,
        "date_fin": date_fin,
    })


# ---------------- PDF ----------------
from django.shortcuts import render
from django.db.models import Sum
from ventes.models import BonLivraison
from datetime import datetime
from core.models import Societe  # selon ton app

def liste_bons_pdf(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    # Queryset des bons comme avant
    bons = BonLivraison.objects.all()
    if date_debut:
        bons = bons.filter(date__gte=date_debut)
    if date_fin:
        bons = bons.filter(date__lte=date_fin)
    bons = bons.order_by("date")

    totaux = bons.aggregate(
        total_ht=Sum("total_ht"),
        total_rem=Sum("total_rem"),
        base_tva=Sum("base_tva"),
        total_tva=Sum("total_tva"),
        total_ttc=Sum("total_ttc"),
    )
    for k in totaux:
        totaux[k] = totaux[k] or 0

    # Récupérer la société (ex: première)
    societe = Societe.objects.first()

    import datetime
    today = datetime.datetime.now()

    return render(request, "editions/liste_bons_pdf.html", {
        "bons": bons,
        "totaux": totaux,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "societe": societe,
        "today": today,
    })


#-------------------- Liste des factures

# ---------------- HTML ----------------
from django.shortcuts import render
from django.db.models import Sum
from ventes.models import Facture
from core.models import Societe
import datetime

def liste_factures_impression(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    factures = Facture.objects.all()

    if date_debut:
        factures = factures.filter(date__gte=date_debut)
    if date_fin:
        factures = factures.filter(date__lte=date_fin)

    factures = factures.order_by("date")

    totaux = factures.aggregate(
        total_ht=Sum("total_ht"),
        total_rem=Sum("total_rem"),
        base_tva=Sum("base_tva"),
        total_tva=Sum("total_tva"),
        total_ttc=Sum("total_ttc"),
    )

    for k in totaux:
        totaux[k] = totaux[k] or 0

    societe = Societe.objects.first()
    today = datetime.datetime.now()

    return render(request, "editions/liste_factures_impression.html", {
        "factures": factures,
        "totaux": totaux,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "societe": societe,
        "today": today,
    })

from django.shortcuts import render
from django.db.models import Sum
from ventes.models import Facture  # Remplacer BonLivraison par Facture
from core.models import Societe
import datetime

def liste_factures_pdf(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    # Queryset des factures
    factures = Facture.objects.all()
    if date_debut:
        factures = factures.filter(date__gte=date_debut)
    if date_fin:
        factures = factures.filter(date__lte=date_fin)
    factures = factures.order_by("date")

    totaux = factures.aggregate(
        total_ht=Sum("total_ht"),
        total_rem=Sum("total_rem"),
        base_tva=Sum("base_tva"),
        total_tva=Sum("total_tva"),
        total_ttc=Sum("total_ttc"),
    )
    for k in totaux:
        totaux[k] = totaux[k] or 0

    societe = Societe.objects.first()
    today = datetime.datetime.now()

    return render(request, "editions/liste_factures_pdf.html", {
        "factures": factures,
        "totaux": totaux,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "societe": societe,
        "today": today,
    })

#--------------------------------------- 

# ----------------Factures achats  HTML ----------------
from django.shortcuts import render
from django.db.models import Sum
from achats.models import FactureAchat
from core.models import Societe
import datetime

def liste_factachats_impression(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    factures = FactureAchat.objects.all()

    if date_debut:
        factures = factures.filter(date__gte=date_debut)
    if date_fin:
        factures = factures.filter(date__lte=date_fin)

    factures = factures.order_by("date")

    totaux = factures.aggregate(
        total_ht=Sum("total_ht"),
        total_rem=Sum("total_rem"),
        base_tva=Sum("base_tva"),
        total_tva=Sum("total_tva"),
        total_ttc=Sum("total_ttc"),
    )

    for k in totaux:
        totaux[k] = totaux[k] or 0

    societe = Societe.objects.first()
    today = datetime.datetime.now()

    return render(request, "editions/liste_factachats_impression.html", {
        "factures": factures,
        "totaux": totaux,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "societe": societe,
        "today": today,
    })

def liste_factachats_pdf(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    # Queryset des factures
    factures = FactureAchat.objects.all()
    if date_debut:
        factures = factures.filter(date__gte=date_debut)
    if date_fin:
        factures = factures.filter(date__lte=date_fin)
    factures = factures.order_by("date")

    totaux = factures.aggregate(
        total_ht=Sum("total_ht"),
        total_rem=Sum("total_rem"),
        base_tva=Sum("base_tva"),
        total_tva=Sum("total_tva"),
        total_ttc=Sum("total_ttc"),
    )
    for k in totaux:
        totaux[k] = totaux[k] or 0

    societe = Societe.objects.first()
    today = datetime.datetime.now()

    return render(request, "editions/liste_factachats_pdf.html", {
        "factures": factures,
        "totaux": totaux,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "societe": societe,
        "today": today,
    })

#--------------------------------------- 
