from django.db.models import Q

from order.models.coupons import CouponUsage


class CouponNotApplicable(Exception):
    pass


class InsufficientStock(Exception):
    pass


def validate_and_apply_coupon(user, coupon, cart_items):
    usage_count = CouponUsage.objects.filter(coupon=coupon).count()
    if coupon.max_usage is not None and usage_count >= coupon.max_usage:
        raise CouponNotApplicable("ظرفیت استفاده از این کد تخفیف تکمیل شده است.")

    if CouponUsage.objects.filter(user=user, coupon=coupon).exists():
        raise CouponNotApplicable("شما قبلاً از این کد تخفیف استفاده کرده‌اید.")

    coupon_products = coupon.products.all()
    coupon_categories = coupon.categories.all()

    if not coupon_products.exists() and not coupon_categories.exists():
        eligible_items = cart_items
    else:
        eligible_items = cart_items.filter(
            Q(product__in=coupon_products) | Q(product__category__in=coupon_categories)
        )

    if not eligible_items.exists():
        raise CouponNotApplicable(
            "این کد تخفیف برای محصولات سبد خرید شما قابل استفاده نیست."
        )

    eligible_total = sum(
        item.product.final_price * item.quantity for item in eligible_items
    )

    if eligible_total < coupon.minimum_order_price:
        raise CouponNotApplicable(
            f"حداقل مبلغ محصولات مشمول این کد تخفیف {coupon.minimum_order_price} تومان است."  # noqa : E501
        )

    discount_amount = round(eligible_total * coupon.discount / 100)
    if coupon.max_discount is not None and discount_amount > coupon.max_discount:
        discount_amount = coupon.max_discount

    return eligible_total, discount_amount
