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


def generer_avoir_fournisseur_pdf(avoir):

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
    Avoir Fournisseur: {avoir.numero}
    Fournisseur: {avoir.fournisseur.nom}
    Date: {avoir.date.strftime('%d/%m/%Y')}
    """

    qr = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    qr_image = Image(qr_buffer, 3 * cm, 3 * cm)

    # ======================
    # SOCIETE
    # ======================
    societe = get_societe()

    societe_info = [
        [Paragraph(societe.nom, styles["Heading2"])],
        [Paragraph(f"Adresse : {societe.adresse} - {societe.ville} - {societe.pays}", styles["Normal"])],
        [Paragraph(f"MF      : {societe.matricule_fiscal}", styles["Normal"])],
        [Paragraph(f"Tel     : {societe.telephone}", styles["Normal"])],
        [Paragraph(f"Email   : {societe.email}", styles["Normal"])],
    ]

    elements.append(Spacer(1, 20))
    societe_table = Table(societe_info)

    header_table = Table(
        [[societe_table, qr_image]],
        colWidths=[16 * cm, 4 * cm]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(header_table)

    # ======================
    # TITRE
    # ======================
    elements.append(Paragraph(f"<b>AVOIR FOURNISSEUR N° {avoir.numero}</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Date : {avoir.date.strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ======================
    # FOURNISSEUR
    # ======================
    fournisseur_data = [
        ["Fournisseur", avoir.fournisseur.nom],
        ["Matricule Fiscal", avoir.mf_fournisseur or ""],
        ["Adresse", avoir.adresse_fournisseur or ""],
        ["Téléphone", avoir.telephone_fournisseur or ""],
        ["Email", avoir.email_fournisseur or ""],
    ]

    fournisseur_table = Table(fournisseur_data, colWidths=[5 * cm, 13 * cm])

    fournisseur_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(fournisseur_table)
    elements.append(Spacer(1, 25))

    # ======================
    # LIGNES
    # ======================
    lignes = list(avoir.lignes.all())

    lignes_par_page = 16
    total_lignes = len(lignes)
    pages = (total_lignes // lignes_par_page) + 1

    index = 0

    for page in range(pages):

        data = [["Produit", "Qté", "Prix HT", "TVA %"]]

        for i in range(lignes_par_page):

            if index < total_lignes:
                ligne = lignes[index]

                data.append([
                    str(ligne.produit),
                    f"{ligne.quantite}",
                    f"{ligne.prix_ht:.3f}",
                    f"{ligne.taux_tva}",
                ])

                index += 1
            else:
                data.append(["", "", "", ""])

        table = Table(
            data,
            colWidths=[9 * cm, 3 * cm, 4 * cm, 4 * cm]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]))

        elements.append(table)

        if page < pages - 1:
            elements.append(PageBreak())

    elements.append(Spacer(1, 20))

    # ======================
    # TOTAUX (IDENTIQUE BR)
    # ======================
    total_ht = total_rem = base_tva = total_tva = total_ttc = 0

    for ligne in avoir.lignes.all():

        montant_ht = ligne.quantite * ligne.prix_ht
        rem = montant_ht * (ligne.taux_rem or 0) / 100
        base = montant_ht - rem
        tva = base * (ligne.taux_tva or 0) / 100

        total_ht += montant_ht
        total_rem += rem
        base_tva += base
        total_tva += tva
        total_ttc += base + tva

    totaux_data = [
        ["Total HT", f"{total_ht:.3f} TND"],
        ["Total Remise", f"{total_rem:.3f} TND"],
        ["Base TVA", f"{base_tva:.3f} TND"],
        ["Total TVA", f"{total_tva:.3f} TND"],
        ["Total TTC", f"{total_ttc:.3f} TND"],
    ]

    totaux_table = Table(totaux_data, colWidths=[6 * cm, 5 * cm])

    totaux_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 4), (-1, 4), colors.lightgrey),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))

    elements.append(Spacer(1, 20))
    elements.append(totaux_table)

    # ======================
    # BUILD PDF
    # ======================
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="avoir_fournisseur_{avoir.numero}.pdf"'
    response.write(pdf)

    return response