from django.urls import path
from .views import test_openai_view, run_openai_test

urlpatterns = [
    path('openai-test/', test_openai_view, name='openai-test'),
    path('run-openai-test/', run_openai_test, name='run-openai-test'),
]
