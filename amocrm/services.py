import logging
from datetime import date, time, timedelta

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AmoCRMTokenError(Exception):
    pass


class AmoCRMService:
    BASE_URL = f"https://{settings.AMOCRM_SUBDOMAIN}.amocrm.ru/api/v4"
    TOKEN_LIFETIME_HOURS = 23

    FIELD_TEST_DRIVE_DATE = 1492447  # "План. дата. тест. драйв", тип date_time

    def __init__(self):
        self._token_obj = None
        self.headers = {}
        self._load_token()

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        """raise_for_status с логированием тела ответа."""
        if not response.ok:
            logger.error(
                "AmoCRM API error %s %s\nURL: %s\nBody: %s",
                response.status_code,
                response.reason,
                response.url,
                response.text,
            )
            response.raise_for_status()

    # ─────────────────────────────────────────
    # Токены
    # ─────────────────────────────────────────

    def _load_token(self) -> None:
        """Загружает токен из БД, при необходимости обновляет."""
        from .models import AmoCRMToken

        token = AmoCRMToken.objects.order_by("-updated_at").first()
        if not token:
            raise AmoCRMTokenError("Токен AmoCRM не найден в базе данных.")

        if self._is_token_expired(token):
            logger.info("Access token устарел — обновляем.")
            token = self._refresh_token(token)

        self._token_obj = token
        self.headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json",
        }

    def _is_token_expired(self, token) -> bool:
        threshold = timezone.now() - timedelta(hours=self.TOKEN_LIFETIME_HOURS)
        return token.updated_at <= threshold

    def _refresh_token(self, token):
        """Получает новую пару токенов через refresh_token и сохраняет в БД."""
        from .models import AmoCRMToken

        response = requests.post(
            f"https://{settings.AMOCRM_SUBDOMAIN}.amocrm.ru/oauth2/access_token",
            json={
                "client_id": settings.AMOCRM_CLIENT_ID,
                "client_secret": settings.AMOCRM_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": token.refresh_token,
                "redirect_uri": settings.AMOCRM_REDIRECT_URI,
            },
            timeout=10,
        )

        if response.status_code != 200:
            raise AmoCRMTokenError(
                f"Не удалось обновить токен: {response.status_code} {response.text}"
            )

        data = response.json()

        # Обновляем существующую запись (не плодим дубли токенов)
        token.access_token = data["access_token"]
        token.refresh_token = data["refresh_token"]
        token.save(update_fields=["access_token", "refresh_token", "updated_at"])

        logger.info("Токен AmoCRM успешно обновлён.")
        return AmoCRMToken.objects.get(pk=token.pk)  # свежий объект с updated_at

    # ─────────────────────────────────────────
    # Публичные методы — точки входа из задач
    # ─────────────────────────────────────────

    def sync_callback(self, name: str, phone: str, comment: str) -> dict:
        note_lines = [
            "Новый запрос обратного звонка",
            f"Имя: {name}",
            f"Телефон: {phone}",
        ]
        if comment:
            note_lines.append(f"Комментарий: {comment}")

        return self._sync_lead(
            contact_name=name,
            phone=phone,
            phone_enum="MOB",
            lead_name=f"Обратный звонок — {name}",
            note_lines=note_lines,
            task_text=f"Перезвонить: {name} / {phone}",
        )

    def sync_car_application(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        comment: str,
        dealer: str,
        configuration: str,
    ) -> dict:
        full_name = f"{first_name} {last_name}".strip()
        note_lines = [
            "Новая заявка на автомобиль",
            f"Дилер: {dealer}",
            f"Комплектация: {configuration}",
        ]
        if comment:
            note_lines.append(f"Комментарий: {comment}")

        return self._sync_lead(
            contact_name=full_name,
            phone=phone,
            phone_enum="WORK",
            lead_name=f"Заявка на автомобиль — {full_name}",
            note_lines=note_lines,
            task_text=f"Перезвонить: {full_name} / {phone}",
        )

    def sync_test_drive(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        comment: str,
        desired_date: date | None,
        desired_time: time | None,
    ) -> dict:
        full_name = f"{first_name} {last_name}".strip()
        note_lines = ["Новая заявка на тест-драйв"]
        if desired_date:
            note_lines.append(f"Дата: {desired_date.strftime('%d.%m.%Y')}")
        if desired_time:
            note_lines.append(f"Время: {desired_time.strftime('%H:%M')}")
        if comment:
            note_lines.append(f"Комментарий: {comment}")

        custom_fields = self._build_test_drive_date_field(desired_date, desired_time)

        return self._sync_lead(
            contact_name=full_name,
            phone=phone,
            phone_enum="WORK",
            lead_name=f"Тест-драйв — {full_name}",
            note_lines=note_lines,
            task_text=f"Перезвонить: {full_name} / {phone}",
            lead_custom_fields=custom_fields,
        )

    # ─────────────────────────────────────────
    # Общая логика синхронизации
    # ─────────────────────────────────────────

    def _sync_lead(
        self,
        contact_name: str,
        phone: str,
        phone_enum: str,
        lead_name: str,
        note_lines: list[str],
        task_text: str,
        lead_custom_fields: list | None = None,
    ) -> dict:
        """
        1. Ищет контакт по номеру телефона.
        2. Если есть открытая сделка — дописывает примечание.
        3. Если открытой сделки нет — создаёт новую.
        4. В обоих случаях создаёт задачу к сделке.
        """
        contact = self._find_contact_by_phone(phone)

        if contact:
            contact_id = contact["id"]
            logger.info("Найден существующий контакт #%s", contact_id)
            open_lead = self._find_open_lead_by_contact(contact_id)
        else:
            contact_id = self._create_contact(contact_name, phone, phone_enum)
            logger.info("Создан новый контакт #%s", contact_id)
            open_lead = None

        note_text = "\n".join(note_lines)

        if open_lead:
            lead_id = open_lead["id"]
            logger.info("Найдена открытая сделка #%s — добавляем примечание", lead_id)
            self._add_note_to_lead(lead_id, note_text)
            action = "note_added"
        else:
            lead_id = self._create_lead(
                lead_name, contact_id, note_text, lead_custom_fields
            )
            logger.info("Создана новая сделка #%s", lead_id)
            action = "lead_created"

        task_id = self._add_task_to_lead(lead_id, text=task_text)

        return {
            "contact_id": contact_id,
            "lead_id": lead_id,
            "task_id": task_id,
            "action": action,
        }

    # ─────────────────────────────────────────
    # Контакты
    # ─────────────────────────────────────────

    def _find_contact_by_phone(self, phone: str) -> dict | None:
        """Ищет контакт по номеру телефона через поиск AmoCRM."""
        normalized = "".join(filter(str.isdigit, phone))

        response = requests.get(
            f"{self.BASE_URL}/contacts",
            headers=self.headers,
            params={"query": normalized},
            timeout=10,
        )

        if response.status_code == 204:
            return None

        response.raise_for_status()
        contacts = response.json().get("_embedded", {}).get("contacts", [])
        return contacts[0] if contacts else None

    def _create_contact(self, name: str, phone: str, phone_enum: str = "MOB") -> int:
        payload = [
            {
                "name": name,
                "custom_fields_values": [
                    {
                        "field_code": "PHONE",
                        "values": [{"value": phone, "enum_code": phone_enum}],
                    }
                ],
            }
        ]
        response = requests.post(
            f"{self.BASE_URL}/contacts",
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["_embedded"]["contacts"][0]["id"]

    # ─────────────────────────────────────────
    # Сделки
    # ─────────────────────────────────────────

    def _find_open_lead_by_contact(self, contact_id: int) -> dict | None:
        """
        Ищет открытую (не закрытую) сделку у контакта.
        Статус 142 — «Успешно реализовано», 143 — «Закрыто и не реализовано».
        """
        response = requests.get(
            f"{self.BASE_URL}/leads",
            headers=self.headers,
            params={
                "query": contact_id,
                "with": "contacts",
                "limit": 50,
            },
            timeout=10,
        )

        if response.status_code == 204:
            return None

        response.raise_for_status()
        leads = response.json().get("_embedded", {}).get("leads", [])

        CLOSED_STATUSES = {142, 143}
        open_leads = [
            lead for lead in leads
            if lead.get("status_id") not in CLOSED_STATUSES
        ]

        if open_leads:
            return max(open_leads, key=lambda lead: lead.get("updated_at", 0))

        return None

    def _create_lead(
        self,
        name: str,
        contact_id: int,
        note_text: str,
        custom_fields: list | None = None,
    ) -> int:
        lead: dict = {
            "name": name,
            "pipeline_id": int(settings.AMOCRM_PIPELINE_ID),
            "status_id": int(settings.AMOCRM_STATUS_ID),
            "_embedded": {
                "contacts": [{"id": contact_id}],
            },
        }
        if custom_fields:
            lead["custom_fields_values"] = custom_fields

        response = requests.post(
            f"{self.BASE_URL}/leads",
            json=[lead],
            headers=self.headers,
            timeout=10,
        )
        self._raise_for_status(response)
        lead_id = response.json()["_embedded"]["leads"][0]["id"]

        if note_text:
            self._add_note_to_lead(lead_id, note_text)

        return lead_id

    # ─────────────────────────────────────────
    # Примечания
    # ─────────────────────────────────────────

    def _add_note_to_lead(self, lead_id: int, text: str) -> None:
        payload = [
            {
                "entity_id": lead_id,
                "note_type": "common",
                "params": {"text": text},
            }
        ]
        response = requests.post(
            f"{self.BASE_URL}/leads/notes",
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()

    # ─────────────────────────────────────────
    # Задачи
    # ─────────────────────────────────────────

    def _add_task_to_lead(
        self,
        lead_id: int,
        text: str = "Обработать заявку",
        responsible_user_id: int | None = None,
        complete_till_hours: int = 24,
    ) -> int:
        complete_till = int(
            (timezone.now() + timedelta(hours=complete_till_hours)).timestamp()
        )

        task: dict = {
            "task_type_id": 1,  # 1 — «Позвонить»
            "text": text,
            "complete_till": complete_till,
            "entity_type": "leads",
            "entity_id": lead_id,
        }

        if responsible_user_id:
            task["responsible_user_id"] = responsible_user_id

        response = requests.post(
            f"{self.BASE_URL}/tasks",
            json=[task],
            headers=self.headers,
            timeout=10,
        )
        self._raise_for_status(response)

        task_id = response.json()["_embedded"]["tasks"][0]["id"]
        logger.info("Создана задача #%s к сделке #%s", task_id, lead_id)
        return task_id

    # ─────────────────────────────────────────
    # Вспомогательные методы
    # ─────────────────────────────────────────

    def _build_test_drive_date_field(
        self, desired_date: date | None, desired_time: time | None
    ) -> list:
        """Формирует custom_fields_values для поля 'План. дата. тест. драйв'."""
        if not desired_date:
            return []

        from datetime import datetime
        from zoneinfo import ZoneInfo

        dt = datetime.combine(
            desired_date,
            desired_time if desired_time else time(0, 0),
            tzinfo=ZoneInfo(settings.TIME_ZONE),
        )
        timestamp = int(dt.timestamp())

        return [
            {
                "field_id": self.FIELD_TEST_DRIVE_DATE,
                "values": [{"value": timestamp}],
            }
        ]
