from dataclasses import dataclass
from typing import Protocol

from app.modules.billing.models import Payment


@dataclass
class PaymentConfirmation:
    status: str  # "approved" | "rejected" | "pending", normalizado por cada adaptador
    amount: int
    currency: str
    gateway_payment_id: str
    external_reference: str | None = None


class BillingProvider(Protocol):
    """Patrón adaptador (ADR-003): cada pasarela implementa esta misma interfaz."""

    def create_checkout(self, payment: Payment) -> str:
        """Devuelve la URL de la pasarela donde la persona paga."""
        ...

    def verify_signature(self, headers: dict, query_params: dict, body: bytes) -> bool:
        """True solo si el aviso viene realmente de esta pasarela."""
        ...

    def extract_event_id(self, headers: dict, query_params: dict, body: bytes) -> str:
        """Identificador del aviso, para descartar repetidos."""
        ...

    def extract_gateway_payment_id(self, headers: dict, query_params: dict, body: bytes) -> str:
        """Identificador del pago para consultar `confirm_payment`."""
        ...

    def confirm_payment(self, gateway_payment_id: str) -> PaymentConfirmation:
        """Consulta a la pasarela (nunca confía solo en el cuerpo del aviso) el estado real."""
        ...
