import hmac
import json

from app.core.config import get_settings
from app.core.errors import AppError
from app.modules.billing.models import Payment
from app.modules.billing.providers.base import PaymentConfirmation

# Resultados simulados por referencia, fijados por el endpoint de desarrollo
# (POST /billing/_dev/fake-approve/{referencia}) o directamente por las pruebas. En memoria, por
# proceso — es una pasarela de desarrollo, ADR-003 la prohíbe en producción.
_simulated_results: dict[str, PaymentConfirmation] = {}


def simulate_result(reference: str, status: str, amount: int, currency: str) -> None:
    _simulated_results[reference] = PaymentConfirmation(
        status=status,
        amount=amount,
        currency=currency,
        gateway_payment_id=reference,
        external_reference=reference,
    )


def clear_simulated_results() -> None:
    _simulated_results.clear()


class FakeBillingProvider:
    """Pasarela simulada para desarrollo y pruebas (ADR-003). Nunca se usa en producción."""

    def create_checkout(self, payment: Payment) -> str:
        settings = get_settings()
        return f"{settings.public_base_url}/billing/fake-checkout/{payment.reference}"

    def verify_signature(self, headers: dict, query_params: dict, body: bytes) -> bool:
        settings = get_settings()
        if not settings.payment_webhook_secret:
            return False  # sin secreto configurado, se rechaza todo (fail-closed).
        signature = headers.get("x-fake-signature", "")
        return hmac.compare_digest(signature, settings.payment_webhook_secret)

    def _body_data(self, body: bytes) -> dict:
        try:
            return json.loads(body) if body else {}
        except ValueError:
            return {}

    def extract_event_id(self, headers: dict, query_params: dict, body: bytes) -> str:
        data = self._body_data(body)
        return str(data.get("event_id") or data.get("reference") or "")

    def extract_gateway_payment_id(self, headers: dict, query_params: dict, body: bytes) -> str:
        return str(self._body_data(body).get("reference") or "")

    def confirm_payment(self, gateway_payment_id: str) -> PaymentConfirmation:
        result = _simulated_results.get(gateway_payment_id)
        if result is None:
            raise AppError(
                502,
                "upstream_unavailable",
                "La pasarela simulada no tiene un resultado para esta referencia. Usa"
                " /billing/_dev/fake-approve/{referencia} primero.",
            )
        return result
