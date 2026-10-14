from collections import Counter

ORDERS_PROCESSED = []

VIP_HIGH_TIER_MIN = 1000
VIP_HIGH_DISCOUNT = 0.15
VIP_BASE_DISCOUNT = 0.10
EMPLOYEE_DISCOUNT = 0.20
REGULAR_MIN_SUBTOTAL = 800
REGULAR_DISCOUNT = 0.05

PROMO10_RATE = 0.10
PROMO20_RATE = 0.20
PROMO20_MIN_SUBTOTAL = 500
VIP50_DISCOUNT_AMOUNT = 50
MAX_DISCOUNT_RATE = 0.25


def calculate_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items if item["qty"] > 0)


def calculate_customer_discount(subtotal, customer_type):
    if customer_type == "vip":
        rate = VIP_HIGH_DISCOUNT if subtotal >= VIP_HIGH_TIER_MIN else VIP_BASE_DISCOUNT
        return subtotal * rate
    if customer_type == "employee":
        return subtotal * EMPLOYEE_DISCOUNT
    if customer_type == "regular" and subtotal >= REGULAR_MIN_SUBTOTAL:
        return subtotal * REGULAR_DISCOUNT
    return 0.0


def calculate_coupon_discount(subtotal, customer_type, coupon):
    if coupon == "PROMO10":
        return subtotal * PROMO10_RATE
    if coupon == "PROMO20" and subtotal >= PROMO20_MIN_SUBTOTAL:
        return subtotal * PROMO20_RATE
    if coupon == "VIP50" and customer_type == "vip":
        return VIP50_DISCOUNT_AMOUNT
    return 0.0


def calculate_discount(subtotal, customer_type, coupon):
    raw_discount = (
        calculate_customer_discount(subtotal, customer_type)
        + calculate_coupon_discount(subtotal, customer_type, coupon)
    )
    return min(raw_discount, subtotal * MAX_DISCOUNT_RATE)


def find_duplicate_products(items):
    counts = Counter(item["name"] for item in items)
    return [name for name, count in counts.items() if count > 1]


def process_order(customer, items, coupon="", state="MG", express=False):
    subtotal = calculate_subtotal(items)
    desconto = calculate_discount(subtotal, customer["type"], coupon)
    valor_com_desconto = subtotal - desconto

    peso = 0
    for produto in items:
        peso += produto.get("weight", 0) * produto["qty"]

    frete = 0

    if subtotal >= 500 and not express:
        frete = 0
    else:
        if state in {"MG", "SP", "RJ", "ES"}:
            frete = 20 + peso * 0.4
        else:
            frete = 35 + peso * 0.6

        if express:
            frete = frete * 1.8

    taxa = 0

    if state == "MG":
        taxa = 0.07
    elif state == "SP":
        taxa = 0.09
    elif state == "RJ":
        taxa = 0.08
    elif state == "ES":
        taxa = 0.07
    else:
        taxa = 0.12

    imposto = valor_com_desconto * taxa

    if customer["type"] == "vip":
        pontos = int((valor_com_desconto + frete + imposto) / 5)
    else:
        pontos = int((valor_com_desconto + frete + imposto) / 10)

    duplicados = find_duplicate_products(items)
    total_final = round(valor_com_desconto + frete + imposto, 2)

    resultado = {
        "customer": customer["name"],
        "subtotal": round(subtotal, 2),
        "discount": round(desconto, 2),
        "shipping": round(frete, 2),
        "tax": round(imposto, 2),
        "total": total_final,
        "points": pontos,
        "duplicate_products": duplicados,
    }

    ORDERS_PROCESSED.append(resultado)

    print("Pedido processado para " + customer["name"])
    print("Subtotal:", subtotal)
    print("Desconto:", desconto)
    print("Frete:", frete)
    print("Imposto:", imposto)
    print("TOTAL:", total_final)

    return resultado