import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AmoCRMTokenError(Exception):
    pass


class AmoCRMService:
    BASE_URL = f"https://{settings.AMOCRM_SUBDOMAIN}.amocrm.ru/api/v4"
    TOKEN_LIFETIME_HOURS = 23

    def __init__(self):
        self._token_obj = None
        self.headers = {}
        self._load_token()

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
    # Публичный метод — точка входа из задачи
    # ─────────────────────────────────────────

    def sync_callback(self, name: str, phone: str, comment: str) -> dict:
        """
        Основной метод:
        1. Ищет контакт по номеру телефона.
        2. Если есть открытая сделка — дописывает примечание.
        3. Если открытой сделки нет — создаёт новую.
        """
        contact = self._find_contact_by_phone(phone)

        if contact:
            contact_id = contact["id"]
            logger.info("Найден существующий контакт #%s", contact_id)
            open_lead = self._find_open_lead_by_contact(contact_id)
        else:
            contact_id = self._create_contact(name, phone)
            logger.info("Создан новый контакт #%s", contact_id)
            open_lead = None

        if open_lead:
            lead_id = open_lead["id"]
            logger.info("Найдена открытая сделка #%s — добавляем примечание", lead_id)
            self._add_note_to_lead(lead_id, name, phone, comment)
            action = "note_added"
        else:
            lead_id = self._create_lead(name, comment, contact_id)
            logger.info("Создана новая сделка #%s", lead_id)
            action = "lead_created"

        return {"contact_id": contact_id, "lead_id": lead_id, "action": action}

    # ─────────────────────────────────────────
    # Контакты
    # ─────────────────────────────────────────

    def _find_contact_by_phone(self, phone: str) -> dict | None:
        """Ищет контакт по номеру телефона через поиск AmoCRM."""
        # Нормализуем: оставляем только цифры для надёжного поиска
        normalized = "".join(filter(str.isdigit, phone))

        response = requests.get(
            f"{self.BASE_URL}/contacts",
            headers=self.headers,
            params={"query": normalized, "with": "leads"},
            timeout=10,
        )

        if response.status_code == 204:  # не найдено
            return None

        response.raise_for_status()
        contacts = response.json().get("_embedded", {}).get("contacts", [])
        return contacts[0] if contacts else None

    def _create_contact(self, name: str, phone: str) -> int:
        payload = [
            {
                "name": name,
                "custom_fields_values": [
                    {
                        "field_code": "PHONE",
                        "values": [{"value": phone, "enum_code": "MOB"}],
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
                "filter[contact_id]": contact_id,
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
        open_leads = [lead for lead in leads if lead.get("status_id") not in CLOSED_STATUSES]

        # Берём самую свежую открытую сделку
        if open_leads:
            return max(open_leads, key=lambda lead: lead.get("updated_at", 0))

        return None

    def _create_lead(self, name: str, comment: str, contact_id: int) -> int:
        payload = [
            {
                "name": f"Обратный звонок — {name}",
                "pipeline_id": settings.AMOCRM_PIPELINE_ID,
                "_embedded": {
                    "contacts": [{"id": contact_id}],
                },
            }
        ]
        response = requests.post(
            f"{self.BASE_URL}/leads",
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        lead_id = response.json()["_embedded"]["leads"][0]["id"]

        # Добавляем комментарий сразу к новой сделке
        if comment:
            self._add_note_to_lead(lead_id, name, "", comment)

        return lead_id

    # ─────────────────────────────────────────
    # Примечания
    # ─────────────────────────────────────────

    def _add_note_to_lead(self, lead_id: int, name: str, phone: str, comment: str) -> None:
        """Добавляет примечание к сделке с данными из заявки."""
        lines = ["Новый запрос обратного звонка"]
        if name:
            lines.append(f"Имя: {name}")
        if phone:
            lines.append(f"Телефон: {phone}")
        if comment:
            lines.append(f"Комментарий: {comment}")

        payload = [
            {
                "entity_id": lead_id,
                "note_type": "common",
                "params": {"text": "\n".join(lines)},
            }
        ]
        response = requests.post(
            f"{self.BASE_URL}/leads/notes",
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
