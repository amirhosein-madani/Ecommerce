from cart.cart import Cart, DBCartAdapter


def get_cart(request):
    if request.user.is_authenticated:
        return DBCartAdapter(request.user)
    return Cart(request.session)
