from django.contrib import admin
from .models import MessageSpec, ReportingEntity, CbcBody, CbcReport, Summary


@admin.register(MessageSpec)
class MessageSpecAdmin(admin.ModelAdmin):
    list_display = (
        "message_ref_id",
        "sending_entity_in",
        "transmitting_country",
        "receiving_country",
        "reporting_period",
    )


@admin.register(ReportingEntity)
class ReportingEntityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tin",
        "country_code",
        "city",
    )


@admin.register(CbcBody)
class CbcBodyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message_spec",
        "reporting_entity",
    )


@admin.register(CbcReport)
class CbcReportAdmin(admin.ModelAdmin):
    list_display = (
        "country_code",
        "total_revenue",
        "profit_loss",
        "tax_paid",
        "employees",
    )


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = (
        "entity_name",
        "country_code",
        "activity",
        "report",
    )