from django.contrib import admin
from django import forms
from .models import AzureOpenAIResource

@admin.register(AzureOpenAIResource)
class AzureOpenAIResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint', 'deployment_id', 'api_version')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'api_key':
            kwargs['widget'] = forms.PasswordInput(render_value=True)
        return super().formfield_for_dbfield(db_field, **kwargs)
