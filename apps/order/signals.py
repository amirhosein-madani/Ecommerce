from django.db.models.signals import post_save
from django.dispatch import receiver

from order.models.coupons import CouponUsage


@receiver(post_save, sender=CouponUsage)
def deactivate_coupon_if_usage_limit_reached(sender, instance, created, **kwargs):
    if not created:
        return

    coupon = instance.coupon

    if coupon.max_usage is None:
        return

    usage_count = coupon.usages.count()

    if usage_count >= coupon.max_usage and coupon.is_active:
        coupon.is_active = False
        coupon.save(update_fields=["is_active"])
