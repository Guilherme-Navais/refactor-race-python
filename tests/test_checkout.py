import pytest
from legacy_checkout import ORDERS_PROCESSED, process_order


@pytest.fixture(autouse=True)
def clear_orders_history():
    ORDERS_PROCESSED.clear()


# ==========================================
# TESTES ORIGINAIS PRESERVADOS
# ==========================================


def test_regular_customer():
    customer = {"name": "Ana", "type": "regular"}
    items = [{"name": "Notebook", "price": 1000.00, "qty": 1, "weight": 2}]

    result = process_order(customer, items, state="MG")

    assert result["subtotal"] == 1000.00
    assert result["discount"] == 50.00
    assert result["shipping"] == 0
    assert result["tax"] == 66.50
    assert result["total"] == 1016.50
    assert result["points"] == 101


def test_vip_customer():
    customer = {"name": "Carlos", "type": "vip"}
    items = [{"name": "Monitor", "price": 600, "qty": 2, "weight": 3}]

    result = process_order(customer, items, state="SP")

    assert result["subtotal"] == 1200
    assert result["discount"] == 180
    assert result["shipping"] == 0
    assert result["tax"] == 91.80
    assert result["total"] == 1111.80
    assert result["points"] == 222


def test_coupon():
    customer = {"name": "Maria", "type": "regular"}
    items = [{"name": "Teclado", "price": 200, "qty": 2, "weight": 1}]

    result = process_order(customer, items, coupon="PROMO10", state="MG")

    assert result["subtotal"] == 400
    assert result["discount"] == 40
    assert result["shipping"] == 20.80
    assert result["tax"] == 25.20
    assert result["total"] == 406.00


def test_duplicate_products():
    customer = {"name": "João", "type": "regular"}
    items = [
        {"name": "Mouse", "price": 100, "qty": 1, "weight": 0.2},
        {"name": "Mouse", "price": 100, "qty": 1, "weight": 0.2},
        {"name": "Teclado", "price": 200, "qty": 1, "weight": 1},
    ]

    result = process_order(customer, items)

    assert result["duplicate_products"] == ["Mouse"]


# ==========================================
# NOVOS TESTES (CENÁRIOS E CASOS LIMITE)
# ==========================================


def test_vip_customer_under_1000_receives_10_percent_discount():
    customer = {"name": "Beatriz", "type": "vip"}
    items = [{"name": "Headset", "price": 500.00, "qty": 1, "weight": 1}]

    result = process_order(customer, items, state="MG")

    assert result["subtotal"] == 500.00
    assert result["discount"] == 50.00
    assert result["points"] == 96


def test_employee_customer_receives_20_percent_discount():
    customer = {"name": "Marcos", "type": "employee"}
    items = [{"name": "Cadeira", "price": 1000.00, "qty": 1, "weight": 10}]

    result = process_order(customer, items, state="RJ")

    assert result["subtotal"] == 1000.00
    assert result["discount"] == 200.00
    assert result["tax"] == 64.00
    assert result["total"] == 864.00


def test_regular_customer_under_800_receives_no_tier_discount():
    customer = {"name": "Lucas", "type": "regular"}
    items = [{"name": "Webcam", "price": 300.00, "qty": 1, "weight": 0.5}]

    result = process_order(customer, items, state="ES")

    assert result["subtotal"] == 300.00
    assert result["discount"] == 0.00
    assert result["shipping"] == 20.20
    assert result["tax"] == 21.00
    assert result["total"] == 341.20


def test_promo20_coupon_applies_when_subtotal_is_at_least_500():
    customer = {"name": "Fernanda", "type": "regular"}
    items = [{"name": "HD Externo", "price": 500.00, "qty": 1, "weight": 0.5}]

    result = process_order(customer, items, coupon="PROMO20", state="MG")

    assert result["discount"] == 100.00


def test_promo20_coupon_is_ignored_when_subtotal_is_under_500():
    customer = {"name": "Fernanda", "type": "regular"}
    items = [{"name": "Pen Drive", "price": 100.00, "qty": 2, "weight": 0.1}]

    result = process_order(customer, items, coupon="PROMO20", state="MG")

    assert result["discount"] == 0.00


def test_vip50_coupon_adds_fixed_discount_only_for_vip_customers():
    vip_customer = {"name": "Roberto", "type": "vip"}
    regular_customer = {"name": "Camila", "type": "regular"}
    items = [{"name": "SSD", "price": 400.00, "qty": 1, "weight": 0.5}]

    vip_result = process_order(vip_customer, items, coupon="VIP50", state="MG")
    regular_result = process_order(regular_customer, items, coupon="VIP50", state="MG")

    assert vip_result["discount"] == 90.00  # 10% (40) + 50 fixo
    assert regular_result["discount"] == 0.00


def test_total_discount_is_capped_at_25_percent_of_subtotal():
    customer = {"name": "Helena", "type": "employee"}  # 20%
    items = [{"name": "Smartphone", "price": 1000.00, "qty": 1, "weight": 0.5}]

    # 20% (employee) + 20% (PROMO20) = 40%, mas o limite máximo é 25% (250.00)
    result = process_order(customer, items, coupon="PROMO20", state="MG")

    assert result["discount"] == 250.00


def test_express_shipping_in_southeast_charges_multiplier_even_over_500():
    customer = {"name": "Diego", "type": "regular"}
    items = [{"name": "Placa de Vídeo", "price": 600.00, "qty": 1, "weight": 5}]

    # Sudeste: (20 + 5 * 0.4) * 1.8 = 22 * 1.8 = 39.60
    result = process_order(customer, items, state="MG", express=True)

    assert result["shipping"] == 39.60


def test_shipping_and_tax_outside_southeast_region():
    customer = {"name": "Patrícia", "type": "regular"}
    items = [{"name": "Impressora", "price": 300.00, "qty": 1, "weight": 10}]

    # Fora do Sudeste (BA): frete = 35 + 10 * 0.6 = 41.00 | imposto = 12% de 300 = 36.00
    result = process_order(customer, items, state="BA", express=False)

    assert result["shipping"] == 41.00
    assert result["tax"] == 36.00
    assert result["total"] == 377.00


def test_items_with_zero_quantity_do_not_affect_subtotal():
    customer = {"name": "Gustavo", "type": "regular"}
    items = [
        {"name": "Cabo HDMI", "price": 50.00, "qty": 2, "weight": 0.2},
        {"name": "Brinde Esgotado", "price": 200.00, "qty": 0, "weight": 0.5},
    ]

    result = process_order(customer, items, state="MG")

    assert result["subtotal"] == 100.00
    assert len(ORDERS_PROCESSED) == 1