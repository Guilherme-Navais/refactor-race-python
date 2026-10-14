from collections import Counter

ORDERS_PROCESSED = []


def calculate_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items if item["qty"] > 0)


def find_duplicate_products(items):
    counts = Counter(item["name"] for item in items)
    return [name for name, count in counts.items() if count > 1]


def process_order(customer, items, coupon="", state="MG", express=False):
    subtotal = calculate_subtotal(items)

    desconto = 0

    if customer["type"] == "vip":
        if subtotal >= 1000:
            desconto = subtotal * 0.15
        else:
            desconto = subtotal * 0.10
    else:
        if customer["type"] == "employee":
            desconto = subtotal * 0.20
        else:
            if customer["type"] == "regular":
                if subtotal >= 800:
                    desconto = subtotal * 0.05

    if coupon == "PROMO10":
        desconto = desconto + subtotal * 0.10

    if coupon == "PROMO20" and subtotal >= 500:
        desconto = desconto + subtotal * 0.20

    if coupon == "VIP50" and customer["type"] == "vip":
        desconto = desconto + 50

    if desconto > subtotal * 0.25:
        desconto = subtotal * 0.25

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