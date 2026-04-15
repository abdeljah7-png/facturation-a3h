# comptes/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm

from .models import Compte
from reglements.models import MouvementCompte
from core.models import Societe
from django.utils.dateparse import parse_date

# ------------------- UTILITAIRE -------------------
def calcul_mouvements_solde(compte, date_debut=None, date_fin=None):
    """
    Retourne mouvements filtrés, report initial, totaux et solde final
    """
    mouvements = MouvementCompte.objects.filter(compte=compte).order_by("date")

    # Report initial avant date_debut
    report = 0
    if date_debut:
        mouvements_avant = mouvements.filter(date__lt=date_debut)
        report = sum(
            m.montant if m.type_mouvement == "entree" else -m.montant
            for m in mouvements_avant
        )

    # Filtrer selon période
    if date_debut:
        mouvements = mouvements.filter(date__gte=date_debut)
    if date_fin:
        mouvements = mouvements.filter(date__lte=date_fin)

    solde = report
    total_debit = 0
    total_credit = 0
    lignes = []

    for m in mouvements:
        debit = m.montant if m.type_mouvement == "entree" else 0
        credit = m.montant if m.type_mouvement == "sortie" else 0
        solde += debit - credit
        total_debit += debit
        total_credit += credit

        # Libellé détaillé si règlement client/fournisseur
        if hasattr(m, "reglement_client") and m.reglement_client:
            libelle = f"Règlement Client RC n°{m.reglement_client.numero}"
        elif hasattr(m, "reglement_fournisseur") and m.reglement_fournisseur:
            libelle = f"Règlement Fournisseur RF n°{m.reglement_fournisseur.numero}"
        else:
            libelle = m.reference or f"MC n°{m.id}"

        lignes.append({
            "date": m.date,
            "libelle": libelle,
            "debit": debit,
            "credit": credit,
            "solde": solde
        })

    return lignes, report, total_debit, total_credit, solde

# ------------------- VUES -------------------
def releve_compte(request, compte_id):
    compte = get_object_or_404(Compte, id=compte_id)
    societe = Societe.objects.first()

    # Récupérer dates depuis le HTML
    date_debut_str = request.GET.get("date_debut")
    date_fin_str = request.GET.get("date_fin")
    date_debut = parse_date(date_debut_str) if date_debut_str else None
    date_fin = parse_date(date_fin_str) if date_fin_str else None

    lignes, report, total_debit, total_credit, solde = calcul_mouvements_solde(
        compte, date_debut, date_fin
    )

    context = {
        "societe": societe,
        "compte": compte,
        "lignes": lignes,
        "report": report,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "solde": solde,
        "date_debut": date_debut_str,
        "date_fin": date_fin_str
    }

    return render(request, "comptes/releve_compte.html", context)


def releve_compte_pdf(request, compte_id):
    compte = get_object_or_404(Compte, id=compte_id)
    societe = Societe.objects.first()

    # Récupérer dates depuis le HTML
    date_debut_str = request.GET.get("date_debut")
    date_fin_str = request.GET.get("date_fin")
    date_debut = parse_date(date_debut_str) if date_debut_str else None
    date_fin = parse_date(date_fin_str) if date_fin_str else None

    lignes, report, total_debit, total_credit, solde = calcul_mouvements_solde(
        compte, date_debut, date_fin
    )

    # Création du PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=releve_compte_{compte.id}.pdf"

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    # Entête société
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*cm, y, societe.nom if societe else "Société")
    y -= 0.6*cm
    p.setFont("Helvetica", 10)
    if societe:
        p.drawString(1*cm, y, societe.adresse or "")
        y -= 0.6*cm
        p.drawString(1*cm, y, "M.F : " + societe.matricule_fiscal or "")
        y -= 0.6*cm

        p.drawString(1*cm, y, f"Tél: {societe.telephone or ''} | Email: {societe.email or ''}")
    y -= 1*cm
    p.setFont("Helvetica-Bold", 14)
    p.drawString(6*cm, y, f"Releve de compte : {compte.libelle or ''}")
    y -= 2*cm

    # Report initial
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2*cm, y, f"Report initial : {report:.3f}")
    y -= 0.6*cm

    # Période
    periode_text = "Période : "
    if date_debut and date_fin:
        periode_text += f"{date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"
    elif date_debut:
        periode_text += f"à partir de {date_debut.strftime('%d/%m/%Y')}"
    elif date_fin:
        periode_text += f"jusqu'à {date_fin.strftime('%d/%m/%Y')}"
    else:
        periode_text += "tous les mouvements"
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y, periode_text)
    y -= 0.8*cm

    # Tableau
    data = [["Date", "Libellé", "Débit", "Crédit", "Solde"]]
    for l in lignes:
        data.append([
            l["date"].strftime("%d/%m/%Y"),
            l["libelle"],
            f"{l['debit']:.3f}" if l["debit"] else "",
            f"{l['credit']:.3f}" if l["credit"] else "",
            f"{l['solde']:.3f}"
        ])
    # Totaux
    data.append(["Totaux", "", f"{total_debit:.3f}", f"{total_credit:.3f}", f"{solde:.3f}"])

    table = Table(data, colWidths=[3*cm, 6*cm, 3*cm, 3*cm, 3*cm])    
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (2,0), (-1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))

    w, h = table.wrapOn(p, width-4*cm, y)
    table.drawOn(p, 1.5*cm, y-h)

    
    
    p.showPage()
    p.save()

    return response