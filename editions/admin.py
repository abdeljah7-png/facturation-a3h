from django.contrib import admin
from django.shortcuts import redirect
from .models import EditionMenu




class EditionMenuAdmin(admin.ModelAdmin):

    # 🔁 Redirection vers dashboard
    def changelist_view(self, request, extra_context=None):
        return redirect('/editions/dashboard-admin/')

    # ❌ empêcher ajout
    def has_add_permission(self, request):
        return False

    # ❌ empêcher modification
    def has_change_permission(self, request, obj=None):
        return False

    # ❌ empêcher suppression
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(EditionMenu, EditionMenuAdmin)

admin.site.site_header = "Application A3H"
admin.site.site_title = "ERP - A3H"
admin.site.index_title = "Tableau de bord ERP - A3H"
