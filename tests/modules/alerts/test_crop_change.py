from fastapi.testclient import TestClient


def _registrar_cosecha(client, farm_id, headers, crop="maiz"):
    return client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": crop, "planting_date": "2026-01-10", "stage": "cosecha"},
        headers=headers,
    )


def test_plan_free_no_recibe_alerta_de_cambio_de_cultivo(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    _registrar_cosecha(client, farm_id, headers)

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    types = {a["type"] for a in response.json()}
    assert "crop_change" not in types


def test_plan_basico_recibe_el_aviso_sin_sugerencia(
    client: TestClient, seeded_crops, producer_with_farm, set_plan
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("alertas@example.com", "basic")
    _registrar_cosecha(client, farm_id, headers)

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    alerts = {a["type"]: a for a in response.json()}
    assert "crop_change" in alerts
    assert alerts["crop_change"]["suggested_crop"] is None


def test_plan_pro_recibe_el_aviso_con_sugerencia(
    client: TestClient, seeded_crops, producer_with_farm, set_plan
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("alertas@example.com", "pro")
    _registrar_cosecha(client, farm_id, headers, crop="maiz")

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    alerts = {a["type"]: a for a in response.json()}
    assert alerts["crop_change"]["suggested_crop"] is not None
    assert alerts["crop_change"]["recommendations"]


def test_plan_pro_sin_recomendacion_disponible(
    client: TestClient, producer_with_farm, set_plan
) -> None:
    """Sin cultivos en el catálogo (no se usa `seeded_crops`), el motor de rotación no tiene con
    qué recomendar: el aviso se crea igual, pero sin sugerencia."""
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("alertas@example.com", "pro")
    _registrar_cosecha(client, farm_id, headers, crop="lo-que-sea")

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    alerts = {a["type"]: a for a in response.json()}
    assert "crop_change" in alerts
    assert alerts["crop_change"]["suggested_crop"] is None
