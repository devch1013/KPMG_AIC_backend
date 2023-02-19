from django.apps import AppConfig
from .main_model.qa_model import QAModel


class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai"
    qa_model = QAModel()
