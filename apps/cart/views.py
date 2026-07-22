from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from cart.cart import Cart
from products.models import Product
from cart.messages import CartMessages

# Create your views here.


class AddToCartView(View):

    def post(self, request, product_id):

        product = get_object_or_404(Product.objects.published(), id=product_id)

        cart = Cart(request.session)

        quantity = request.POST.get("quantity", 1)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return JsonResponse({"error": CartMessages.INVALID_QUANTITY}, status=400)

        if quantity < 1:
            return JsonResponse({"error": CartMessages.QUANTITY_POSITIVE}, status=400)

        current_quantity = cart.get_quantity(product.pk)

        if current_quantity + quantity > product.stock:
            return JsonResponse({"error": CartMessages.NOT_ENOUGH_STOCK}, status=400)

        cart.add(product.pk, quantity, product.final_price)

        return JsonResponse(
            {
                "success": True,
                "message": CartMessages.PRODUCT_ADDED,
                "cart_count": len(cart),
                "total": cart.get_total_price(),
            }
        )


class CartView(TemplateView):
    template_name = "cart/cart-summary.html"


class CartUpdateView(View):

    def post(self, request, product_id):

        cart = Cart(request.session)

        product = get_object_or_404(Product.objects.published(), id=product_id)

        quantity = request.POST.get("quantity")

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": CartMessages.INVALID_QUANTITY},
                status=400,
            )

        if quantity < 1:
            return JsonResponse(
                {"error": CartMessages.QUANTITY_POSITIVE},
                status=400,
            )

        if quantity > product.stock:
            return JsonResponse({"error": CartMessages.NOT_ENOUGH_STOCK}, status=400)

        cart.update(product_id=product_id, quantity=quantity)

        item_total = product.final_price * quantity

        return JsonResponse(
            {
                "success": True,
                "message": CartMessages.PRODUCT_INCREASED,
                "cart_count": len(cart),
                "item_total": item_total,
                "cart_total_price": cart.get_total_price(),
                "total_quantity": len(cart),
            }
        )


class CartRemoveView(View):

    def post(self, request, product_id):

        cart = Cart(request.session)

        product = get_object_or_404(Product.objects.published(), id=product_id)

        cart.remove(product.pk)

        return JsonResponse(
            {
                "success": True,
                "message": CartMessages.PRODUCT_REMOVED,
                "cart_count": len(cart),
                "cart_total_price": str(cart.get_total_price()),
                "total_quantity": len(cart),
            }
        )


class ClearCartView(View):

    def post(self, request):

        cart = Cart(request.session)

        cart.clear()

        return JsonResponse(
            {
                "success": True,
                "message": CartMessages.CART_CLEARED,
                "cart_count": len(cart),
                "cart_total_price": str(cart.get_total_price()),
                "total_quantity": len(cart),
            }
        )
