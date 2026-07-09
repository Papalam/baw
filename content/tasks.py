import logging
from celery import shared_task
from amocrm.services import AmoCRMService, AmoCRMTokenError

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    # Ошибки токена не ретраим — нужно вмешательство человека
    dont_autoretry_for=(AmoCRMTokenError,),
)
def send_callback_to_amocrm(self, callback_id: int) -> None:
    from .models import CallbackRequest

    try:
        callback = CallbackRequest.objects.get(pk=callback_id)
    except CallbackRequest.DoesNotExist:
        logger.error("CallbackRequest #%s не найден", callback_id)
        return

    if callback.is_sent_to_crm:
        logger.info("CallbackRequest #%s уже отправлен, пропускаем", callback_id)
        return

    logger.info("Отправляем CallbackRequest #%s в AmoCRM", callback_id)

    service = AmoCRMService()
    result = service.sync_callback(
        name=callback.name,
        phone=callback.phone,
        comment=callback.comment,
    )

    CallbackRequest.objects.filter(pk=callback_id).update(is_sent_to_crm=True)

    logger.info("CallbackRequest #%s готово. Результат: %s", callback_id, result)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    dont_autoretry_for=(AmoCRMTokenError,),
)
def send_car_application_to_amocrm(self, application_id: int) -> None:
    from .models import CarApplication

    try:
        application = CarApplication.objects.select_related("configuration").get(
            pk=application_id
        )
    except CarApplication.DoesNotExist:
        logger.error("CarApplication #%s не найдена", application_id)
        return

    if application.is_sent_to_crm:
        logger.info("CarApplication #%s уже отправлена, пропускаем", application_id)
        return

    logger.info("Отправляем CarApplication #%s в AmoCRM", application_id)

    service = AmoCRMService()
    result = service.sync_car_application(
        first_name=application.first_name,
        last_name=application.last_name,
        phone=application.phone,
        comment=application.comment,
        dealer=application.dealer,
        configuration=str(application.configuration),
    )

    CarApplication.objects.filter(pk=application_id).update(is_sent_to_crm=True)
    logger.info("CarApplication #%s готово. Результат: %s", application_id, result)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    dont_autoretry_for=(AmoCRMTokenError,),
)
def send_test_drive_to_amocrm(self, request_id: int) -> None:
    from .models import TestDriveRequest

    try:
        test_drive = TestDriveRequest.objects.get(pk=request_id)
    except TestDriveRequest.DoesNotExist:
        logger.error("TestDriveRequest #%s не найден", request_id)
        return

    if test_drive.is_sent_to_crm:
        logger.info("TestDriveRequest #%s уже отправлен, пропускаем", request_id)
        return

    logger.info("Отправляем TestDriveRequest #%s в AmoCRM", request_id)

    service = AmoCRMService()
    result = service.sync_test_drive(
        first_name=test_drive.first_name,
        last_name=test_drive.last_name,
        phone=test_drive.phone,
        comment=test_drive.comment,
        desired_date=test_drive.desired_date,
        desired_time=test_drive.desired_time,
    )

    TestDriveRequest.objects.filter(pk=request_id).update(is_sent_to_crm=True)
    logger.info("TestDriveRequest #%s готово. Результат: %s", request_id, result)
