from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import qrcode
from core.utils import get_societe

def generer_demande_pdf(demande):

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
    Demande de prix: {demande.numero}
    Fournisseur: {demande.fournisseur.nom}
    Date: {demande.date.strftime('%d/%m/%Y')}
    """

    qr = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    qr_image = Image(qr_buffer, 3 * cm, 3 * cm)

    # ======================
    # ENTETE SOCIETE
    # ======================
    societe = get_societe()

    societe_info = [
        [Paragraph(societe.nom, styles["Heading2"])],
        [Paragraph(
            f"Adresse : {societe.adresse} - {societe.ville} - {societe.pays}",
            styles["Normal"]
        )],
        [Paragraph(
            f"MF      : {societe.matricule_fiscal}",
            styles["Normal"]
        )],
        [Paragraph(
            f"Tel     : {societe.telephone}",
            styles["Normal"]
        )],
        [Paragraph(
            f"Email   : {societe.email}",
            styles["Normal"]
        )],
    ]

    societe_table = Table(societe_info)

    header_table = Table(
        [[societe_table, qr_image]],
        colWidths=[16 * cm, 4 * cm]
    )

    elements.append(header_table)

    elements.append(Paragraph(f"<b>DEMANDE DE PRIX N° {demande.numero}</b>", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # ======================
    # FOURNISSEUR
    # ======================
    fournisseur_data = [
        ["Fournisseur", demande.fournisseur.nom],
        ["Matricule Fiscal", demande.fournisseur.matricule_fiscal or ""],
        ["Adresse", demande.fournisseur.adresse or ""],
        ["Téléphone", demande.fournisseur.telephone or ""],
        ["Email", demande.fournisseur.email or ""],
    ]

    fournisseur_table = Table(fournisseur_data, colWidths=[5 * cm, 13 * cm])

    fournisseur_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(fournisseur_table)
    elements.append(Spacer(1, 20))

    # ======================
    # LIGNES DEMANDE
    # ======================
    data = [["Produit", "Quantité"]]

    for ligne in demande.lignes.all():
        data.append([
            str(ligne.produit),
            ligne.quantite
        ])

    table = Table(data, colWidths=[14 * cm, 4 * cm])

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]))

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="demande_{demande.numero}.pdf"'
    response.write(pdf)

    return response