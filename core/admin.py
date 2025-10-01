from django.contrib import admin
from .models import Baby, Allergy

@admin.register(Baby)
class BabyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    filter_horizontal = ('allergies',)

admin.site.register(Allergy)
