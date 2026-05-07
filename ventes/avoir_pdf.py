from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import qrcode

from core.utils import get_societe
from .models import AvoirClient


def generer_avoir_pdf(avoir):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=10,
        bottomMargin=30,
    )

    elements = []
    styles = getSampleStyleSheet()

    # ======================
    # QR CODE
    # ======================
    qr_data = f"""
    Avoir: {avoir.numero}
    Client: {avoir.client.nom if avoir.client else ""}
    Date: {avoir.date.strftime('%d/%m/%Y')}
    Total TTC: {avoir.total_ttc}
    """

    qr = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    qr_image = Image(qr_buffer, 3*cm, 3*cm)

    # ======================
    # SOCIETE
    # ======================
    societe = get_societe()

    societe_info = [
        [Paragraph(societe.nom, styles["Heading2"])],
        [Paragraph(f"Adresse : {societe.adresse} - {societe.ville} - {societe.pays}", styles["Normal"])],
        [Paragraph(f"MF : {societe.matricule_fiscal}", styles["Normal"])],
        [Paragraph(f"Tel : {societe.telephone}", styles["Normal"])],
        [Paragraph(f"Email : {societe.email}", styles["Normal"])],
    ]

    societe_table = Table(societe_info)

    header = Table(
        [[societe_table, qr_image]],
        colWidths=[13*cm, 8*cm]
    )

    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 10))

    # ======================
    # TITRE
    # ======================
    elements.append(Paragraph(f"<b>Avoir Client N° {avoir.numero}</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Date : {avoir.date.strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ======================
    # CLIENT
    # ======================
    client_data = [
        ["Client", avoir.client.nom if avoir.client else ""],
        ["Matricule Fiscal", getattr(avoir, "mf_client", "")],
        ["Adresse", getattr(avoir, "adresse_client", "")],
        ["Téléphone", getattr(avoir, "telephone_client", "")],
        ["Email", getattr(avoir, "email_client", "")],
    ]

    client_table = Table(client_data, colWidths=[5*cm, 13*cm])

    client_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(client_table)
    elements.append(Spacer(1, 20))

    # ======================
    # LIGNES (IDENTIQUE BL)
    # ======================
    lignes = list(avoir.lignes.all())

    data = [["Produit", "Qté", "Prix HT", "Rem %", "TVA %", "Total TTC"]]

    total_ht = 0
    total_rem = 0
    base_tva = 0
    total_tva = 0
    total_ttc = 0

    for l in lignes:

        qte = float(l.quantite or 0)
        prix = float(l.prix_ht or 0)

        ht = qte * prix

        rem = ht * float(getattr(l, "taux_rem", 0) or 0) / 100
        base = ht - rem
        tva = base * float(getattr(l, "taux_tva", 0) or 0) / 100
        ttc = base + tva

        total_ht += ht
        total_rem += rem
        base_tva += base
        total_tva += tva
        total_ttc += ttc

        data.append([
            str(l.produit),
            f"{qte}",
            f"{prix:.3f}",
            f"{getattr(l,'taux_rem',0)}",
            f"{getattr(l,'taux_tva',0)}",
            f"{ttc:.3f}",
        ])

    table = Table(
        data,
        colWidths=[7*cm, 2*cm, 3*cm, 2*cm, 2*cm, 3*cm]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ======================
    # 🔥 TABLEAU TOTAL IDENTIQUE BL
    # ======================
    total_data = [
        ["Total HT", f"{total_ht:.3f} TND"],
        ["Total Remise", f"{total_rem:.3f} TND"],
        ["Base TVA", f"{base_tva:.3f} TND"],
        ["Total TVA", f"{total_tva:.3f} TND"],
        ["Total TTC", f"{total_ttc:.3f} TND"],
    ]

    total_table = Table(total_data, colWidths=[6*cm, 4*cm])

    total_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 4), (-1, 4), colors.lightgrey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))

    elements.append(total_table)

    # ======================
    # BUILD
    # ======================
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="avoir_{avoir.numero}.pdf"'
    response.write(pdf)

    return response