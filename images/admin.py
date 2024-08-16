from django.contrib import admin
from .models import GeneratedImage


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'image', 'task_id', 'created_at')
    search_fields = ('prompt',)

