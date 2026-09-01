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
        return cart if cart else {}

    def add(self, product_id, quantity):
        product_id = str(product_id)

        if product_id in self.cart:
            self.cart[product_id]["quantity"] += quantity
        else:
            self.cart[product_id] = {"quantity": quantity}

        self._save()

    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self._save()

    def clear(self):
        cache.delete(self.key)
        self.cart = {}

    def update(self, product_id, quantity):
        product_id = str(product_id)

        if product_id in self.cart:
            self.cart[product_id]["quantity"] = quantity
            self._save()

    def _save(self):
        cache.set(self.key, self.cart, timeout=60 * 60 * 24 * 7)

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def __iter__(self):

        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids)

        for product in products:

            cart_item = self.cart[str(product.id)]

            item = {
                "product_obj": product,
                "product_id": product.id,
                "quantity": cart_item["quantity"],
                "price": product.final_price,
                "total_price": (product.final_price * cart_item["quantity"]),
            }

            yield item

    def get_total_price(self):

        total = Decimal("0")

        for item in self:
            total += item["total_price"]

        return total

    def get_quantity(self, product_id):

        return self.cart.get(str(product_id), {}).get("quantity", 0)


# -------------------------------
# Database Cart
# -------------------------------


class DBCartAdapter:
    def __init__(self, user):

        self.user = user

        self.db_cart, _ = DBCart.objects.get_or_create(user=user)

    def add(self, product_id, quantity):

        item, created = DBCartItem.objects.get_or_create(
            cart=self.db_cart,
            product_id=product_id,
            defaults={"quantity": quantity},
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

        total = Decimal("0")

        for item in self:
            total += item["total_price"]

        return total

    def __len__(self):

        return sum(item.quantity for item in self.db_cart.items.all())

    def __iter__(self):

        items = self.db_cart.items.select_related("product")

        for item in items:

            yield {
                "product_obj": item.product,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.product.final_price,
                "total_price": (item.product.final_price * item.quantity),
            }
