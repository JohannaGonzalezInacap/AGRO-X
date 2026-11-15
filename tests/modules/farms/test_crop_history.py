from fastapi.testclient import TestClient

from tests.modules.farms.conftest import FARM_PAYLOAD


def _crear_parcela(client: TestClient, headers: dict) -> str:
    response = client.post("/farms", json=FARM_PAYLOAD, headers=headers)
    return response.json()["id"]


def test_registrar_cultivo_vuelve_no_vigente_al_anterior(
    client: TestClient, producer_headers: dict
) -> None:
    farm_id = _crear_parcela(client, producer_headers)

    primero = client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "maiz", "planting_date": "2026-01-10", "stage": "cosecha"},
        headers=producer_headers,
    )
    assert primero.status_code == 201
    assert primero.json()["current"] is True

    segundo = client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "poroto", "planting_date": "2026-06-01", "stage": "recien_plantada"},
        headers=producer_headers,
    )
    assert segundo.status_code == 201
    assert segundo.json()["current"] is True

    historial = client.get(f"/farms/{farm_id}/crop-history", headers=producer_headers).json()
    vigentes = [h for h in historial if h["current"]]
    assert len(vigentes) == 1
    assert vigentes[0]["crop"] == "poroto"


def test_cambiar_solo_la_etapa_no_crea_historial_nuevo(
    client: TestClient, producer_headers: dict
) -> None:
    farm_id = _crear_parcela(client, producer_headers)
    client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "tomate", "planting_date": "2026-01-10", "stage": "floracion"},
        headers=producer_headers,
    )

    respuesta = client.patch(
        f"/farms/{farm_id}/crop-history/current",
        json={"stage": "fruto"},
        headers=producer_headers,
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["stage"] == "fruto"

    historial = client.get(f"/farms/{farm_id}/crop-history", headers=producer_headers).json()
    assert len(historial) == 1


def test_borrar_parcela_borra_su_historial(client: TestClient, producer_headers: dict) -> None:
    farm_id = _crear_parcela(client, producer_headers)
    client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "maiz", "planting_date": "2026-01-10", "stage": "cosecha"},
        headers=producer_headers,
    )

    client.delete(f"/farms/{farm_id}", headers=producer_headers)

    historial = client.get(f"/farms/{farm_id}/crop-history", headers=producer_headers)
    assert historial.status_code == 404
