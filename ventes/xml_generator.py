import xml.etree.ElementTree as ET
from django.http import HttpResponse
from datetime import datetime

from core.models import Societe
from ventes.models import Facture
from cbc.models import MessageSpec, ReportingEntity, CbcBody, CbcReport, Summary


def generer_facture_xml(facture):

    societe = Societe.objects.first()
    messagespec = MessageSpec.objects.first()

    root = ET.Element("CBC_OECD")

    # =========================
    # MessageSpec
    # =========================

    msg = ET.SubElement(root, "MessageSpec")

    ET.SubElement(msg, "SendingEntityIN").text = messagespec.sending_entity_in
    ET.SubElement(msg, "TransmittingCountry").text = messagespec.transmitting_country
    ET.SubElement(msg, "ReceivingCountry").text = messagespec.receiving_country
    ET.SubElement(msg, "MessageType").text = "CBC"
    ET.SubElement(msg, "MessageRefId").text = messagespec.message_ref_id
    ET.SubElement(msg, "ReportingPeriod").text = str(messagespec.reporting_period)
    ET.SubElement(msg, "Timestamp").text = datetime.now().isoformat()

    # =========================
    # ReportingEntity
    # =========================

    reporting = ReportingEntity.objects.first()

    body = ET.SubElement(root, "CbcBody")

    reporting_xml = ET.SubElement(body, "ReportingEntity")

    ET.SubElement(reporting_xml, "ResCountryCode").text = reporting.country_code

    tin = ET.SubElement(reporting_xml, "TIN")
    tin.text = societe.matricule_fiscal
    tin.set("issuedBy", reporting.country_code)

    ET.SubElement(reporting_xml, "Name").text = societe.nom

    address = ET.SubElement(reporting_xml, "Address")

    ET.SubElement(address, "Street").text = societe.adresse
    ET.SubElement(address, "City").text = societe.ville
    ET.SubElement(address, "CountryCode").text = reporting.country_code

    # =========================
    # CbcReport
    # =========================

    reports = CbcReport.objects.all()

    for report in reports:

        report_xml = ET.SubElement(body, "CbcReport")

        ET.SubElement(report_xml, "ResCountryCode").text = report.country_code

        # Revenues
    #    revenues = ET.SubElement(report_xml, "Revenues")
        revenues = ET.SubElement(report_xml, "Revenues")

        unrelated = getattr(report, "unrelated_revenue", 0)
        related = getattr(report, "related_revenue", 0)
        total = getattr(report, "total_revenue", unrelated + related)

        ET.SubElement(revenues, "Unrelated").text = str(unrelated)
        ET.SubElement(revenues, "Related").text = str(related)
        ET.SubElement(revenues, "Total").text = str(total)
        ET.SubElement(report_xml, "ProfitOrLoss").text = str(report.profit_loss)

        ET.SubElement(report_xml, "ProfitOrLoss").text = str(getattr(report, "profit_loss", 0))
        ET.SubElement(report_xml, "IncomeTaxPaid").text = str(getattr(report, "tax_paid", 0))
        ET.SubElement(report_xml, "IncomeTaxAccrued").text = str(getattr(report, "tax_accrued", 0))
        ET.SubElement(report_xml, "Capital").text = str(getattr(report, "capital", 0))
        ET.SubElement(report_xml, "Earnings").text = str(getattr(report, "earnings", 0))
        ET.SubElement(report_xml, "NbEmployees").text = str(getattr(report, "employees", 0))
        ET.SubElement(report_xml, "TangibleAssets").text = str(getattr(report, "assets", 0))
        # =========================
        # Summary
        # =========================

        summaries = Summary.objects.filter(report=report)

        for s in summaries:

            summary = ET.SubElement(report_xml, "Summary")

            ET.SubElement(summary, "EntityName").text = s.entity_name
            ET.SubElement(summary, "CountryCode").text = s.country_code
            ET.SubElement(summary, "MainBusinessActivity").text = s.activity

    # =========================
    # Génération XML
    # =========================

    tree = ET.ElementTree(root)

    response = HttpResponse(content_type="application/xml")

    response["Content-Disposition"] = "attachment; filename=cbc_report.xml"

    tree.write(response, encoding="utf-8", xml_declaration=True)

    return response