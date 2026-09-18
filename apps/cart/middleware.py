from django.contrib import messages
from django.core.cache import cache

from products.models import Product

from .cart import Cart, DBCartAdapter


class CartMergeMiddleware:
    """Merges a guest session's Redis cart into the logged-in user's
    database cart, once per session.

    Why the guest cart is snapshotted *before* get_response() runs:
    Django rotates the session key on login (a security measure against
    session-fixation attacks). Cart's Redis key is built from
    session.session_key, so constructing a fresh Cart(request.session)
    *after* login would compute a different key — the guest cart data
    would appear to have vanished, even though it's still sitting under
    the old key. Capturing it up front avoids that.

    Why the merge is claimed via cache.add() instead of a session flag:
    request.session is loaded into memory per-request and only written
    back at the end of the request. Two near-simultaneous requests right
    after login (e.g. a double-clicked login button) would each see
    cart_merged=False in their own copy of the session and could both
    proceed to merge, double-adding quantities. cache.add() is atomic
    across requests/processes — only the first caller to add a given key
    succeeds — so it works as a reliable "claim this merge" lock even
    under concurrent requests.
    """

    MERGE_CLAIM_TIMEOUT = 60  # seconds; long enough to cover one merge

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        was_authenticated = request.user.is_authenticated
        session_cart = Cart(request.session)
        cart_snapshot = dict(session_cart.cart)
        # Captured before get_response(): the key the guest cart is
        # actually stored under, before login can rotate session_key.
        pre_login_session_key = request.session.session_key

        response = self.get_response(request)

        just_logged_in = not was_authenticated and request.user.is_authenticated

        if request.user.is_authenticated and not request.session.get("cart_merged"):

            if just_logged_in:
                data_to_merge = cart_snapshot
                claim_key = f"cart_merge_claim_{pre_login_session_key}"
            else:
                data_to_merge = dict(Cart(request.session).cart)
                claim_key = f"cart_merge_claim_{request.session.session_key}"

            # Atomic claim: succeeds for exactly one concurrent request.
            # A losing request skips the merge here — it's safe to do so
            # because the winning request performs it instead.
            claimed = cache.add(claim_key, "1", timeout=self.MERGE_CLAIM_TIMEOUT)

            if claimed:
                self._merge(request, data_to_merge)

                if just_logged_in and cart_snapshot:
                    session_cart.clear()

            # Mark the session as merged regardless of which request won
            # the claim — from this session's point of view, the merge
            # has happened (or is being handled) either way.
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
