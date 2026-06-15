from django.contrib import admin

from .models import Application, Opportunity


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    readonly_fields = ("user", "message", "created")


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "openings", "is_open", "created")
    list_filter = ("is_open",)
    list_editable = ("is_open",)
    search_fields = ("title", "description", "skills")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ApplicationInline]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "user", "status", "created")
    list_filter = ("status", "opportunity")
    list_editable = ("status",)
    search_fields = ("user__email", "opportunity__title")
