from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
from django.utils.dateparse import parse_date
from .models import Client
from reglements.models import MouvementCompte  # Même modèle pour mouvements
from core.models import Societe
from django.shortcuts import render, get_object_or_404
from .models import Client
from django.utils.timezone import now
from ventes.models import BonLivraison,Facture # adapte si besoin
from reglements.models import ReglementClient
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from .models import Client
from ventes.models import BonLivraison
from reglements.models import ReglementClient
from decimal import Decimal
from django.db.models import Sum
from core.utils import get_societe

from django.http import JsonResponse
from .models import Client
from django.http import JsonResponse
from .models import Client

#--------   Relevé client

# ------------------- UTILITAIRE -------------------


from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def client_info(request, client_id):
    client = Client.objects.get(id=client_id)
    return JsonResponse({
        "id": client.id,
        "nom": client.nom,
        "adresse": client.adresse,
        "telephone": client.telephone,
        "email": client.email,
        "solde_initial": float(client.solde_initial),  # 🔥 important
        "date_creation": client.date_creation.strftime("%Y-%m-%d %H:%M:%S")  # 🔥 important
    })

def calcul_releve_client(client, date_debut=None, date_fin=None):
    bons = BonLivraison.objects.filter(client=client)
    reglements = ReglementClient.objects.filter(client=client)

    report = Decimal(client.solde_initial or 0)

    if date_debut:
        debit_avant = bons.filter(date__lt=date_debut).aggregate(total=Sum('total_ttc'))['total'] or 0
        credit_avant = reglements.filter(date__lt=date_debut).aggregate(total=Sum('montant'))['total'] or 0
        report += Decimal(debit_avant) - Decimal(credit_avant)

        # Filtrer dans la période
        bons = bons.filter(date__gte=date_debut)
        reglements = reglements.filter(date__gte=date_debut)
        if date_fin:
            bons = bons.filter(date__lte=date_fin)
            reglements = reglements.filter(date__lte=date_fin)

    mouvements = []
    for b in bons:
        mouvements.append({
            "date": b.date,
            "libelle": f"Bon n°{b.numero}",
            "debit": Decimal(b.total_ttc or 0),
            "credit": Decimal(0)
        })
    for r in reglements:
        mouvements.append({
            "date": r.date,
            "libelle": f"Règlement n°{r.numero}",
            "debit": Decimal(0),
            "credit": Decimal(r.montant or 0)
        })

    mouvements.sort(key=lambda x: x["date"])

    # Solde et lignes
    lignes = []
    solde = report

    if date_debut:
        lignes.append({
            "date": date_debut,
            "libelle": "REPORT INITIAL",
            "debit": Decimal(0),
            "credit": Decimal(0),
            "solde": report
        })

    total_debit = Decimal(0)
    total_credit = Decimal(0)

    for m in mouvements:
        solde += m["debit"] - m["credit"]
        m["solde"] = solde
        lignes.append(m)
        total_debit += m["debit"]
        total_credit += m["credit"]

    return lignes, solde, report, total_debit, total_credit


def releve_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    # Conversion string -> date
    if date_debut:
        date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
    if date_fin:
        date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

    # Récupération des lignes, solde, report et totaux
    lignes, solde, report, total_debit, total_credit = calcul_releve_client(client, date_debut, date_fin)

    return render(request, "clients/releve_client.html", {
        "client": client,
        "lignes": lignes,
        "solde": solde,
        "report": report,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "date_debut": date_debut.strftime("%Y-%m-%d") if date_debut else "",
        "date_fin": date_fin.strftime("%Y-%m-%d") if date_fin else "",
        "now": now()
    })


def releve_client_pdf(request, client_id):

    client = get_object_or_404(Client, id=client_id)

    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    if date_debut:
        date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
    if date_fin:
        date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

    lignes, solde, report, total_debit, total_credit = calcul_releve_client(
        client, date_debut, date_fin
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="releve_client_{client.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=0*cm,   # 👈 plus d’espace pour header société
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    elements = []
    styles = getSampleStyleSheet()

    # 🏢 SOCIÉTÉ
    societe = get_societe()

    if not societe:
        raise Exception("Aucune société définie")

    societe_info = [
        [Paragraph(f"<b>{societe.nom}</b>", styles["Heading2"])],
        [Paragraph(f"{societe.adresse} - {societe.ville} - {societe.pays}", styles["Normal"])],
        [Paragraph(f"MF : {societe.matricule_fiscal}", styles["Normal"])],
        [Paragraph(f"Tel : {societe.telephone}", styles["Normal"])],
        [Paragraph(f"Email : {societe.email}", styles["Normal"])],
    ]

    table_societe = Table(societe_info, colWidths=[500])

    elements.append(Spacer(1, 20))
    elements.append(table_societe)

    # 📄 TITRE
    elements.append(Paragraph("<b>Relevé Client</b>", styles['Title']))
    elements.append(Spacer(1, 10))

    # 👤 CLIENT
    elements.append(Paragraph(f"Client : {client.nom}", styles['Normal']))
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))

    if date_debut and date_fin:
        elements.append(Paragraph(
            f"Période : {date_debut.strftime('%d/%m/%Y')} - {date_fin.strftime('%d/%m/%Y')}",
            styles['Normal']
        ))

    elements.append(Paragraph(f"Report initial : {report:.3f}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # 📊 TABLE
    data = [["Date", "Libellé", "Débit", "Crédit", "Solde"]]

    for m in lignes:
        data.append([
            m["date"].strftime("%d/%m/%Y"),
            m["libelle"],
            f"{m['debit']:.3f}",
            f"{m['credit']:.3f}",
            f"{m['solde']:.3f}",
        ])

    data.append([
        "Totaux", "",
        f"{total_debit:.3f}",
        f"{total_credit:.3f}",
        f"{solde:.3f}"
    ])

    table = Table(data, colWidths=[3*cm, 6*cm, 3*cm, 3*cm, 3*cm])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0, len(data)-1), (-1, len(data)-1), colors.lightgrey),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"<b>Solde final : {solde:.3f}</b>", styles['Normal']))

    doc.build(elements)
    return response