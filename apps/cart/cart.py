import time
from contextlib import contextmanager
from decimal import Decimal

from django.core.cache import cache

from products.models import Product

from cart.models import Cart as DBCart, CartItem as DBCartItem


class CartLockTimeout(Exception):
    """Raised when a cart-level lock could not be acquired in time.

    A caller that gets this should treat the operation as failed (e.g.
    show the user a "please try again" message) rather than silently
    proceeding without the lock, which would reintroduce the race this
    lock exists to prevent.
    """


class Cart:
    """Redis-backed cart for guest (unauthenticated) users.

    Internal representation in the cache is a plain dict keyed by
    product ID as a string:
        {"1": {"quantity": 4}, "2": {"quantity": 7}}
    Price is intentionally never stored here — it's always read live
    from the product at iteration time (see __iter__), so the cart
    always reflects the current price rather than a cached one.
    """

    LOCK_TIMEOUT = 5  # seconds a held lock auto-expires after
    LOCK_WAIT_TIMEOUT = 2  # seconds to keep retrying to acquire the lock
    LOCK_RETRY_INTERVAL = 0.05

    def __init__(self, session):
        self.session = session

        if not self.session.session_key:
            self.session.create()

        self.key = f"cart_{self.session.session_key}"
        self.lock_key = f"{self.key}_lock"
        self.cart = self._get_cart()

    def _get_cart(self):
        cart = cache.get(self.key)
        return cart if cart else {}

    @contextmanager
    def _locked(self):
        """Serialize read-modify-write access to this cart's cache entry.

        Uses cache.add() as an atomic "set if not exists" mutex, which
        works with any Django cache backend (not just Redis-specific
        commands like HINCRBY). Without this, two near-simultaneous
        requests for the same guest session — a double click, or two
        open tabs — could both read the same cart state, modify it
        independently in Python, and the second write would silently
        overwrite the first's change instead of combining with it.
        """
        acquired = False
        end_time = time.monotonic() + self.LOCK_WAIT_TIMEOUT

        while time.monotonic() < end_time:
            if cache.add(self.lock_key, "1", timeout=self.LOCK_TIMEOUT):
                acquired = True
                break
            time.sleep(self.LOCK_RETRY_INTERVAL)

        if not acquired:
            raise CartLockTimeout(
                f"Could not acquire lock for cart '{self.key}' in time."
            )

        try:
            # Re-read the latest state now that we hold the lock — another
            # request may have changed it while we were waiting for it.
            self.cart = self._get_cart()
            yield
        finally:
            cache.delete(self.lock_key)

    def add(self, product_id, quantity):
        product_id = str(product_id)

        with self._locked():
            if product_id in self.cart:
                self.cart[product_id]["quantity"] += quantity
            else:
                self.cart[product_id] = {"quantity": quantity}

            self._save()

    def remove(self, product_id):
        product_id = str(product_id)

        with self._locked():
            if product_id in self.cart:
                del self.cart[product_id]
                self._save()

    def update(self, product_id, quantity):
        product_id = str(product_id)

        with self._locked():
            if product_id in self.cart:
                self.cart[product_id]["quantity"] = quantity
                self._save()

    def clear(self):
        with self._locked():
            cache.delete(self.key)
            self.cart = {}

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
