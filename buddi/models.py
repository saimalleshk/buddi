# buddi/models.py

from django.db import models

class AzureOpenAIResource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    endpoint = models.URLField(help_text="Base URL for the Azure OpenAI resource.")
    api_key = models.CharField(max_length=255)
    deployment_id = models.CharField(max_length=100, help_text="Name of the deployment in Azure OpenAI.")
    api_version = models.CharField(max_length=50, default='2023-12-01-preview')

    def __str__(self):
        return self.name
