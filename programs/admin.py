from django.contrib import admin

from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "is_published", "goal_amount", "raised_amount", "order")
    list_filter = ("is_featured", "is_published")
    list_editable = ("is_featured", "is_published", "order")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
