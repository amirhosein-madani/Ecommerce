from .cart import Cart


def cart_processor(request):

    cart = Cart(request.session)

    return {
        "cart": cart,
        "total_quantity": len(cart),
        "total_price": cart.get_total_price(),
    }
