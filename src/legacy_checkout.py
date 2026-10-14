from collections import Counter

ORDERS_PROCESSED = []

SOUTHEAST_STATES = {"MG", "SP", "RJ", "ES"}
TAX_RATES = {
    "MG": 0.07,
    "SP": 0.09,
    "RJ": 0.08,
    "ES": 0.07,
}
DEFAULT_TAX_RATE = 0.12

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

FREE_SHIPPING_MIN_SUBTOTAL = 500
SOUTHEAST_BASE_SHIPPING = 20
SOUTHEAST_WEIGHT_FACTOR = 0.4
OTHER_BASE_SHIPPING = 35
OTHER_WEIGHT_FACTOR = 0.6
EXPRESS_SHIPPING_MULTIPLIER = 1.8

VIP_POINTS_DIVISOR = 5
DEFAULT_POINTS_DIVISOR = 10


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


def calculate_shipping(items, subtotal, state, express):
    if subtotal >= FREE_SHIPPING_MIN_SUBTOTAL and not express:
        return 0.0

    total_weight = sum(item.get("weight", 0) * item["qty"] for item in items)

    if state in SOUTHEAST_STATES:
        shipping = SOUTHEAST_BASE_SHIPPING + total_weight * SOUTHEAST_WEIGHT_FACTOR
    else:
        shipping = OTHER_BASE_SHIPPING + total_weight * OTHER_WEIGHT_FACTOR

    return shipping * EXPRESS_SHIPPING_MULTIPLIER if express else shipping


def calculate_tax(discounted_amount, state):
    tax_rate = TAX_RATES.get(state, DEFAULT_TAX_RATE)
    return discounted_amount * tax_rate


def calculate_loyalty_points(total_amount, customer_type):
    divisor = VIP_POINTS_DIVISOR if customer_type == "vip" else DEFAULT_POINTS_DIVISOR
    return int(total_amount / divisor)


def find_duplicate_products(items):
    counts = Counter(item["name"] for item in items)
    return [name for name, count in counts.items() if count > 1]


def print_order_summary(customer_name, subtotal, discount, shipping, tax, total):
    print(f"Pedido processado para {customer_name}")
    print("Subtotal:", subtotal)
    print("Desconto:", discount)
    print("Frete:", shipping)
    print("Imposto:", tax)
    print("TOTAL:", total)


def process_order(customer, items, coupon="", state="MG", express=False):
    customer_type = customer["type"]
    customer_name = customer["name"]

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, customer_type, coupon)
    discounted_amount = subtotal - discount

    shipping = calculate_shipping(items, subtotal, state, express)
    tax = calculate_tax(discounted_amount, state)

    raw_total = discounted_amount + shipping + tax
    final_total = round(raw_total, 2)
    points = calculate_loyalty_points(raw_total, customer_type)
    duplicates = find_duplicate_products(items)

    result = {
        "customer": customer_name,
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "shipping": round(shipping, 2),
        "tax": round(tax, 2),
        "total": final_total,
        "points": points,
        "duplicate_products": duplicates,
    }

    ORDERS_PROCESSED.append(result)
    print_order_summary(customer_name, subtotal, discount, shipping, tax, final_total)

    return result