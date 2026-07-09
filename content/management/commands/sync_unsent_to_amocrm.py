from django.core.management.base import BaseCommand

from content.models import CallbackRequest, CarApplication, TestDriveRequest
from content.tasks import (
    send_callback_to_amocrm,
    send_car_application_to_amocrm,
    send_test_drive_to_amocrm,
)


class Command(BaseCommand):
    help = "Ставит в очередь Celery все записи, не отправленные в AmoCRM"

    def handle(self, *args, **options):
        models = [
            (CallbackRequest, send_callback_to_amocrm, "CallbackRequest"),
            (CarApplication, send_car_application_to_amocrm, "CarApplication"),
            (TestDriveRequest, send_test_drive_to_amocrm, "TestDriveRequest"),
        ]

        for model, task, label in models:
            ids = list(model.objects.filter(is_sent_to_crm=False).values_list("pk", flat=True))
            for pk in ids:
                task.delay(pk)
            self.stdout.write(f"{label}: поставлено в очередь {len(ids)} записей")

        self.stdout.write(self.style.SUCCESS("Готово"))
