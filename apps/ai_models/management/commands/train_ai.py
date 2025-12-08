from django.core.management.base import BaseCommand
from apps.ai_models.forecasting import ai_engine

class Command(BaseCommand):
    help = 'Train Data'

    def handle(self, *args, **kwargs):
        try:
            ai_engine.train()
            self.stdout.write(self.style.SUCCESS('Successfully trained AI model!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Training failed: {str(e)}'))