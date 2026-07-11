from django import template

from products.models import Product

register = template.Library()


@register.inclusion_tag("includes/latest-products.html")
def latest_products():
    products = Product.objects.published().order_by("-created_at")[:8]

    return {
        "latest_products": products,
    }


@register.inclusion_tag("includes/similar-products.html")
def similar_products(product):
    product_categories = product.category.all()

    products = (
        Product.objects.published()
        .filter(category__in=product_categories)
        .exclude(id=product.id)
        .distinct()
        .order_by("-created_at")[:4]
    )

    return {
        "similar_products": products,
    }
