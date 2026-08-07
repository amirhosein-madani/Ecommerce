# cart/middleware.py

from django.contrib import messages

from products.models import Product

from .cart import Cart, DBCartAdapter


class CartMergeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        was_authenticated = request.user.is_authenticated
        session_cart = Cart(request.session)
        cart_snapshot = dict(session_cart.cart)

        response = self.get_response(request)

        just_logged_in = not was_authenticated and request.user.is_authenticated

        if request.user.is_authenticated and not request.session.get("cart_merged"):

            data_to_merge = (
                cart_snapshot if just_logged_in else dict(Cart(request.session).cart)
            )

            self._merge(request, data_to_merge)

            if just_logged_in and cart_snapshot:
                session_cart.clear()

            request.session["cart_merged"] = True

        return response

    def _merge(self, request, cart_snapshot):
        if not cart_snapshot:
            return

        db_cart = DBCartAdapter(request.user)

        for product_id, item in cart_snapshot.items():
            product = Product.objects.filter(pk=int(product_id)).first()

            if not product:
                continue

            current_db_quantity = db_cart.get_quantity(product.pk)
            session_quantity = item["quantity"]
            combined_quantity = current_db_quantity + session_quantity

            allowed_to_add = min(session_quantity, product.stock - current_db_quantity)

            if allowed_to_add > 0:
                db_cart.add(
                    product_id=product.pk,
                    quantity=allowed_to_add,
                )

            if combined_quantity > product.stock:
                messages.warning(
                    request,
                    f"تعداد «{product.title}» به‌خاطر محدودیت موجودی به {product.stock} کاهش یافت.",  # noqa: E501
                )
