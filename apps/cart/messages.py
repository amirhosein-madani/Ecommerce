from django.utils.translation import gettext_lazy as _


class CartMessages:
    PRODUCT_ADDED = _("محصول به سبد خرید اضافه شد")
    INVALID_QUANTITY = _("تعداد وارد شده معتبر نیست")
    PRODUCT_REMOVED = _("محصول از سبد حذف شد")
    QUANTITY_POSITIVE = _("تعداد باید بیشتر از صفر باشد")
    NOT_ENOUGH_STOCK = _("موجودی محصول کافی نیست")
    PRODUCT_INCREASED = _("تعداد محصول تغیر کرد")
    CART_CLEARED = _("محصولات با موفقیت حذف شدند")
