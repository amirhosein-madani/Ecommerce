from django.core.cache import cache
from products.models import Product
from decimal import Decimal
from cart.models import Cart as DBCart, CartItem as DBCartItem

# cart_1 = {
#     '1' : {'quantity' : 4 , 'price' : '100.00'},
#     '2' : {'quantity' : 7 , 'price' : '100.00'}
# }


class Cart:

    def __init__(self, session):
        self.session = session

        if not self.session.session_key:
            self.session.create()

        self.key = f"cart_{self.session.session_key}"
        self.cart = self._get_cart()

    def _get_cart(self):
        cart = cache.get(self.key)
        if not cart:
            return {}
        return cart

    def add(self, product_id, quantity, price):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]["quantity"] += quantity
        else:
            self.cart[product_id] = {"quantity": quantity, "price": str(price)}
        self._save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self._save()

    def clear(self):
        cache.delete(self.key)
        self.cart = {}

    def _save(self):
        cache.set(self.key, self.cart, timeout=60 * 60 * 24 * 7)

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            float(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def __iter__(self):
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            item = self.cart[str(product.id)].copy()

            item["product_obj"] = product
            item["product_id"] = product.id
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]

            yield item

    def get_quantity(self, product_id):
        return self.cart.get(str(product_id), {}).get("quantity", 0)

    def update(self, product_id, quantity):
        product_id = str(product_id)

        if product_id in self.cart:
            self.cart[product_id]["quantity"] = quantity
            self._save()


class DBCartAdapter:

    def __init__(self, user):
        self.user = user
        self.db_cart, _ = DBCart.objects.get_or_create(user=user)

    def add(self, product_id, quantity, price):
        item, created = DBCartItem.objects.get_or_create(
            cart=self.db_cart,
            product_id=product_id,
            defaults={"quantity": quantity, "price": Decimal(str(price))},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

    def remove(self, product_id):
        DBCartItem.objects.filter(cart=self.db_cart, product_id=product_id).delete()

    def clear(self):
        self.db_cart.items.all().delete()

    def update(self, product_id, quantity):
        DBCartItem.objects.filter(cart=self.db_cart, product_id=product_id).update(
            quantity=quantity
        )

    def get_quantity(self, product_id):
        item = self.db_cart.items.filter(product_id=product_id).first()
        return item.quantity if item else 0

    def get_total_price(self):
        return sum(
            item.price * item.quantity
            for item in self.db_cart.items.select_related("product")
        )

    def __len__(self):
        return sum(item.quantity for item in self.db_cart.items.all())

    def __iter__(self):
        for item in self.db_cart.items.select_related("product"):
            yield {
                "product_obj": item.product,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
                "total_price": item.price * item.quantity,
            }
