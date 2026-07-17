from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from cart.cart import Cart
from products.models import Product

# Create your views here.


class AddToCartView(View):

    def post(self, request, product_id):

        product = get_object_or_404(Product.objects.published(), id=product_id)

        cart = Cart(request.session)

        quantity = request.POST.get("quantity", 1)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid quantity"}, status=400)

        if quantity < 1:
            return JsonResponse({"error": "Quantity must be positive"}, status=400)

        current_quantity = cart.get_quantity(product.pk)

        if current_quantity + quantity > product.stock:
            return JsonResponse({"error": "Not enough stock"}, status=400)
        cart.add(product.pk, quantity, product.final_price)
        print(cart.cart)
        return JsonResponse(
            {"success": True, "cart_count": len(cart), "total": cart.get_total_price()}
        )


class CartView(TemplateView):
    template_name = "cart/cart-summary.html"
