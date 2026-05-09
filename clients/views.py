# =========================
# DJANGO
# =========================
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from decimal import Decimal
from datetime import datetime

from ventes.models import BonLivraison, AvoirClient
from reglements.models import ReglementClient
# =========================
# MODELS
# =========================
from .models import Client
from ventes.models import BonLivraison, Facture, AvoirClient
from reglements.models import ReglementClient, MouvementCompte
from core.models import Societe
from ventes.models import BonLivraison, AvoirClient
from reglements.models import ReglementClient
from decimal import Decimal
# =========================
# DBF
# =========================
from dbfread import DBF

# =========================
# PYTHON
# =========================
from decimal import Decimal
from datetime import datetime

# =========================
# DJANGO ORM
# =========================
from django.db.models import Sum

# =========================
# UTILS
# =========================
from core.utils import get_societe

# =========================
# REPORTLAB
# =========================
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet

#--------   Relevé client

# ------------------- UTILITAIRE -------------------

def client_info(request, client_id):
    client = Client.objects.get(id=client_id)

    return JsonResponse({
        "nom": client.nom,
        "adresse": client.adresse,
        "telephone": client.telephone,
        "email": client.email,
        "matricule_fiscal": client.matricule_fiscal,
    })



from decimal import Decimal


def calcul_releve_client(client, date_debut=None, date_fin=None):

    bons = BonLivraison.objects.filter(client=client)
    avoirs = AvoirClient.objects.filter(client=client)
    reglements = ReglementClient.objects.filter(client=client)

    report = Decimal(client.solde_initial or 0)

    # =========================
    # REPORT UNIQUEMENT AVANT DATE
    # =========================
    if date_debut:

        report_bons = bons.filter(date__lt=date_debut)
        report_avoirs = avoirs.filter(date__lt=date_debut)
        report_regs = reglements.filter(date__lt=date_debut)

        report += (
            sum(Decimal(b.total_ttc or 0) for b in report_bons)
            - sum(Decimal(a.total_ttc or 0) for a in report_avoirs)
            - sum(Decimal(r.montant or 0) for r in report_regs)
        )

        # période filtrée
        bons = bons.filter(date__gte=date_debut)
        avoirs = avoirs.filter(date__gte=date_debut)
        reglements = reglements.filter(date__gte=date_debut)

    if date_fin:
        bons = bons.filter(date__lte=date_fin)
        avoirs = avoirs.filter(date__lte=date_fin)
        reglements = reglements.filter(date__lte=date_fin)

    # =========================
    # MOUVEMENTS (SEULEMENT PÉRIODE)
    # =========================
    mouvements = []

    for b in bons:
        mouvements.append({
            "date": b.date,
            "libelle": f" {b.numero}",
            "debit": Decimal(b.total_ttc or 0),
            "credit": Decimal(0),
            "lignes": b.lignes.all()
        })

    for a in avoirs:
        mouvements.append({
            "date": a.date,
            "libelle": f"{a.numero}",
            "debit": Decimal(0),
            "credit": Decimal(a.total_ttc or 0),
            "lignes": a.lignes.all()
        })

    for r in reglements:
        mouvements.append({
            "date": r.date,
            "libelle": f"Règlement n° {r.numero}",
            "debit": Decimal(0),
            "credit": Decimal(r.montant or 0),
            "lignes": []
        })

    mouvements.sort(key=lambda x: x["date"])

    # =========================
    # SOLDE
    # =========================
    lignes = []
    solde = report

    total_debit = Decimal(0)
    total_credit = Decimal(0)

    if date_debut:
        lignes.append({
            "date": date_debut,
            "libelle": "REPORT",
            "debit": 0,
            "credit": 0,
            "solde": solde,
            "lignes": []
        })

    for m in mouvements:
        solde += m["debit"] - m["credit"]
        m["solde"] = solde
        lignes.append(m)

        total_debit += m["debit"]
        total_credit += m["credit"]

    return lignes, solde, report, total_debit, total_credit


def releve_client(request, client_id):

    try:
        client = get_object_or_404(Client, id=client_id)

        date_debut = request.GET.get("date_debut")
        date_fin = request.GET.get("date_fin")


        lignes, solde, report, total_debit, total_credit = calcul_releve_client(
            client, date_debut, date_fin
        )

        return render(request, "clients/releve_client.html", {
            "client": client,
            "lignes": lignes,
            "solde": solde,
            "report": report,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "date_debut": date_debut,
            "date_fin": date_fin,
            "now": now()
        })

    except Exception as e:
        return HttpResponse(f"ERREUR RELEVE CLIENT : {e}")


def releve_client_pdf(request, client_id):

    client = get_object_or_404(Client, id=client_id)

    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    # =========================
    # SAFE PARSING UNIQUE (IMPORTANT)
    # =========================
    def parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            try:
                return parser.parse(value).date()
            except:
                return None

    date_debut = parse_date(date_debut)
    date_fin = parse_date(date_fin)

    # =========================
    # CALCUL (IDENTIQUE HTML)
    # =========================
    lignes, solde, report, total_debit, total_credit = calcul_releve_client(
        client, date_debut, date_fin
    )

    # =========================
    # PDF RESPONSE
    # =========================
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="releve_{client.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=0*cm
    )
    elements = []
    styles = getSampleStyleSheet()

    # =========================
    # SOCIETE (VISIBLE FIX)
    # =========================
    societe = get_societe()


    societe = get_societe()

    societe_info = [
        [Paragraph(f"<b>{societe.nom}</b>", styles["Heading2"])],
        [Paragraph(
            f"Adresse : {societe.adresse} - {societe.ville} - {societe.pays}",
            styles["Normal"]
        )],
        [Paragraph(f"MF : {societe.matricule_fiscal}", styles["Normal"])],
        [Paragraph(f"Tel : {societe.telephone}", styles["Normal"])],
        [Paragraph(f"Email : {societe.email}", styles["Normal"])],
    ]

    elements.append(Spacer(1, 15))

    societe_table = Table(
        societe_info,
        colWidths=[18*cm]   # ✔ largeur propre A4
    )

    societe_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    elements.append(societe_table)

    elements.append(Spacer(1, 10))

    # =========================
    # HEADER CLIENT
    # =========================

    elements.append(Paragraph(
        f"<b>Client :</b> {client.nom}",
        styles["Normal"]
    ))

    if date_debut and date_fin:
        elements.append(
            Paragraph(
                f"Période: {date_debut.strftime('%d/%m/%Y')} → {date_fin.strftime('%d/%m/%Y')}",
                styles["Normal"]
            )
        )

    elements.append(Paragraph(f"Report initial: {report:.3f}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # =========================
    # TABLE PRINCIPALE
    # =========================
    data = [["Date", "Libellé", "Débit", "Crédit", "Solde"]]

    for m in lignes:

        data.append([
            m["date"].strftime("%d/%m/%Y"),
            m["libelle"],
            f"{m['debit']:.3f}",
            f"{m['credit']:.3f}",
            f"{m['solde']:.3f}",
        ])

        # =========================
        # DÉTAILS PRODUITS (FIX IMPORTANT)
        # =========================
        for l in m.get("lignes", []):
            data.append([
                "",
                f"   • {l.quantite} x {l.produit}",
                "",
                "",
                ""
            ])

    # =========================
    # TOTAL FINAL
    # =========================
    data.append([
        "TOTAL",
        "",
        f"{total_debit:.3f}",
        f"{total_credit:.3f}",
        f"{solde:.3f}"
    ])

    table = Table(
        data,
        colWidths=[
            3*cm,   # Date
            8*cm,   # Libellé (plus large)
            3*cm,   # Débit
            3*cm,   # Crédit
            3*cm    # Solde
        ]
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
    ]))

    elements.append(table)

   
    elements.append(Spacer(1, 6))

    from reportlab.lib.styles import ParagraphStyle

    solde_style = ParagraphStyle(
        "solde_style",
        parent=styles["Normal"],
        fontSize=14,
        leading=4,
        spaceBefore=4,
    )

    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"<b>Solde Final : {solde:.3f} TND</b>",
        solde_style
    ))
    elements.append(Spacer(1, 6))

    doc.build(elements)
    return response