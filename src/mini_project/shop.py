class Discount:

    def __init__(self, type: str):
        self.type = type

    def get_discount_amount(self, total_price: int) -> int:
        return total_price * 0


class RateDiscount(Discount):

    def __init__(self, rate: float, max_amount: int):
        super().__init__("rate")
        self.rate = rate
        self.max_amount = max_amount

    def get_discount_amount(self, total_price: int) -> int:
        discount_amount = int(total_price * self.rate)
        return min(discount_amount, self.max_amount)


class FixedDiscount(Discount):

    def __init__(self, amount: float, min_total: int):
        super().__init__("fixed")
        self.amount = amount
        self.min_total = min_total

    def get_discount_amount(self, total_price: int) -> int:
        if total_price >= self.min_total:
            return self.amount
        return 0


class Coupon:

    coupons: list["Coupon"] = []

    def __init__(self, code: str, discount: Discount, name: str = "쿠폰 없음"):
        self.code = code
        self.discount = discount
        self.name = name


class Product:

    _id_counter = 1
    products: list["Product"] = []

    def __init__(self, name, price, stock):
        self.id = Product._id_counter
        Product._id_counter += 1
        self.name: str = name
        self.price: int = price
        self.stock: int = stock

    def __str__(self):
        return f"{self.name}: ${self.price:.2f}"

    def display_registered_items(self):
        for product in self.products:
            if product.stock == 0:
                print(f"{product.id}. {product.name} - {product.price}원 (품절)")
            else:
                print(
                    f"{product.id}. {product.name} - {product.price}원 (재고: {product.stock})"
                )

    def deduct_stock(self, quantity: int):
        if self.stock < quantity:
            raise ValueError(f"재고가 부족합니다. (담을 수 있는 수량: {self.stock}개)")
        self.stock -= quantity


class Cart:

    _id_counter = 1

    def __init__(self):
        self.id = Cart._id_counter
        Cart._id_counter += 1
        self.items: list[tuple[Product, int]] = []
        self.total_price: int = 0
        self._coupon: Coupon = Coupon("", Discount("none"))
        self.discount_amount: int = 0
        self.final_price: int = 0
        self.delivery_fee: int = 0

    @property
    def coupon(self) -> Coupon:
        return self._coupon

    @coupon.setter
    def coupon(self, value: Coupon) -> None:
        if value is not None and not isinstance(value, Coupon):
            raise ValueError("쿠폰은 Coupon 객체여야 합니다.")
        self._coupon = value

    def add_item(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("품절된 상품입니다.")
        if product.stock < quantity:
            raise ValueError(
                f"재고가 부족합니다. (담을 수 있는 수량: {product.stock}개)"
            )
        self.items.append((product, quantity))

    def add_items(self, products: list[tuple[Product, int]]):
        for product, quantity in products:
            self.add_item(product, quantity)

    def remove_item(self, product: Product):
        for item in self.items:
            if item[0] == product:
                product.stock += item[1]
                self.items.remove(item)
                return
        raise ValueError(f"장바구니에 없는 제품: {product.name}")

    def calculate_total_price(self):
        self.total_price = sum(
            product.price * quantity for product, quantity in self.items
        )
        return self.total_price

    def calculate_delivery_fee(self) -> int:
        if self.total_price >= 30000:
            self.delivery_fee = 0
        else:
            self.delivery_fee = 3000
        return self.delivery_fee

    def calculate_final_price(self) -> int:
        self.calculate_total_price()
        self.calculate_delivery_fee()
        if self._coupon:
            self.discount_amount = self._coupon.discount.get_discount_amount(
                self.total_price
            )
        else:
            self.discount_amount = 0
        self.final_price = self.total_price + self.delivery_fee - self.discount_amount
        return self.final_price

    def display_receipt(self) -> None:
        print("-" * 20)
        for product, quantity in self.items:
            print(
                f"{product.name:<15} x {quantity:<5}  ${product.price * quantity:<10}"
            )
        print("-" * 20)
        print(f"상품 합계 ${self.total_price:.2f}")
        print(f"할인 ${self.discount_amount:.2f}")
        print(f"배송비 ${self.delivery_fee:.2f}")
        print(f"결제 금액 ${self.final_price:.2f}")
        print("-" * 20)

    def reset_cart(self) -> None:
        self.items.clear()
        self.total_price = 0
        self._coupon = Coupon("", Discount("none"))
        self.discount_amount = 0
        self.final_price = 0
        self.delivery_fee = 0


class Payment:

    _id_counter = 1

    def __init__(self, cart: Cart):
        self.id = Payment._id_counter
        Payment._id_counter += 1
        self.cart = cart

    def process_payment(self) -> None:
        self.cart.display_receipt()
        for product, quantity in self.cart.items:
            product.deduct_stock(quantity)
        self.cart.reset_cart()


# ---

# 기본 상품 등록
products = [
    Product("무선 이어폰", 89_000, 3),
    Product("텀블러", 15_000, 10),
    Product("보조배터리", 32_000, 5),
    Product("마우스패드", 9_000, 0),
    Product("USB 허브", 18_000, 4),
]

Product.products.extend(products)

# 기본 쿠폰 등록
coupons = [
    Coupon("10% 할인", RateDiscount(0.1, 5_000), "10% 할인 (최대 5,000원)"),
    Coupon(
        "5천원 할인",
        FixedDiscount(3_000, 20_000),
        "3,000원 할인 (20,000원 이상 구매 시)",
    ),
]

Coupon.coupons.extend(coupons)

# 장바구니 생성
cart = Cart()

# 쿠폰 생성


# ---

while True:
    print("-" * 20)
    print("1. 상품목록 2. 담기 3. 빼기 4. 장바구니 5. 쿠폰 6. 결제 q.종료")
    print("-" * 20)
    choice = input("선택: ")

    if choice == "1":
        Product.display_registered_items(Product)
    if choice == "2":
        choice_product_id = int(input("상품 번호: "))
        choice_quantity = int(input("수량: "))
        cart.add_item(choice_product_id, choice_quantity)
        print(
            f"{products[choice_product_id - 1].name} {choice_quantity}개를 담았습니다."
        )
    if choice == "3":
        choice_product_id = int(input("상품 번호: "))
        cart.remove_item(choice_product_id)
        print(f"{products[choice_product_id - 1].name}을 장바구니에서 제거했습니다.")

    if choice == "4":
        cart.display_receipt()

    if choice == "5":
        Coupon.display_registered_coupons(Coupon)
        coupon_number = int(input("쿠폰 번호: "))
        cart.apply_coupon(coupon_number)

    if choice == "6":
        payment = Payment(cart)
        payment.process_payment()
        print("결제가 완료되었습니다. 감사합니다!")

    if choice == "q":
        break
