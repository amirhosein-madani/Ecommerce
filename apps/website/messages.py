
from django.utils.translation import gettext_lazy as _


class ContactUsMessages:
    RATE_LIMIT = _("شما یه تازگی پیام ارسال کردید حداقل دو دقیقه منتظر بمانید")
    SUCCESS = _("پیام شما با موفقیت ارسال شد.")


class NewsletterMessages:
    ALREADY_SUBSCRIBED = _("این ایمیل قبلاً ثبت شده است.")
    SUCCESS = _("ایمیل شما با موفقیت ثبت شد.")