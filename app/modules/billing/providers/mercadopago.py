import hashlib
import hmac
import json

import httpx

from app.core.config import get_settings
from app.core.errors import AppError
from app.modules.billing.models import Payment
from app.modules.billing.providers.base import PaymentConfirmation

# Formato de firma y ruta de confirmación verificados contra la documentación vigente de
# Mercado Pago (2026-11-15) antes de programar esta fase, según exige ADR-003. Los nombres de los
# campos de monto y moneda en la respuesta de /v1/payments/{id} (transaction_amount, currency_id)
# son los habituales de su API, pero no se confirmaron hoy contra una respuesta real — mismo
# pendiente que ya existía en spec/seguridad/pagos-pci.md ("revisar la documentación vigente...
# antes de producción").
_STATUS_MAP = {"approved": "approved", "rejected": "rejected"}


def _parse_signature_header(header_value: str) -> tuple[str | None, str | None]:
    parts = dict(
        item.split("=", 1) for item in header_value.split(",") if "=" in item
    )
    return parts.get("ts"), parts.get("v1")


class MercadoPagoProvider:
    """Adaptador real, en modo de pruebas (ADR-003)."""

    def create_checkout(self, payment: Payment) -> str:
        # Checkout Pro real: requiere crear una "preference" en la API de Mercado Pago. No
        # implementado todavía (no hay cuenta de pruebas real, pendiente desde la Fase 0); se
        # deja la interfaz lista para cuando exista.
        raise AppError(
            502,
            "upstream_unavailable",
            "El adaptador real de Mercado Pago todavía no puede iniciar un pago (falta la cuenta"
            " de pruebas, pendiente desde la Fase 0). Usa el proveedor 'fake' por ahora.",
        )

    def verify_signature(self, headers: dict, query_params: dict, body: bytes) -> bool:
        settings = get_settings()
        if not settings.payment_webhook_secret:
            return False
        ts, v1 = _parse_signature_header(headers.get("x-signature", ""))
        request_id = headers.get("x-request-id", "")
        data_id = query_params.get("data.id", "")
        if not ts or not v1 or not data_id:
            return False
        manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
        expected = hmac.new(
            settings.payment_webhook_secret.encode("utf-8"),
            manifest.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, v1)

    def extract_event_id(self, headers: dict, query_params: dict, body: bytes) -> str:
        try:
            data = json.loads(body) if body else {}
        except ValueError:
            data = {}
        notification_id = data.get("id")
        if notification_id is not None:
            return str(notification_id)
        return str(query_params.get("data.id", ""))

    def extract_gateway_payment_id(self, headers: dict, query_params: dict, body: bytes) -> str:
        return str(query_params.get("data.id", ""))

    def confirm_payment(self, gateway_payment_id: str) -> PaymentConfirmation:
        settings = get_settings()
        url = f"{settings.mercadopago_api_base_url}/v1/payments/{gateway_payment_id}"
        headers = {"Authorization": f"Bearer {settings.mercadopago_access_token}"}
        try:
            response = httpx.get(url, headers=headers, timeout=settings.external_api_timeout_seconds)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AppError(
                502, "upstream_unavailable", "Mercado Pago no respondió. Intenta más tarde."
            ) from exc

        payload = response.json()
        status = _STATUS_MAP.get(payload.get("status"), "pending")
        return PaymentConfirmation(
            status=status,
            amount=int(payload.get("transaction_amount", 0)),
            currency=str(payload.get("currency_id", "")),
            gateway_payment_id=gateway_payment_id,
            external_reference=payload.get("external_reference"),
        )
