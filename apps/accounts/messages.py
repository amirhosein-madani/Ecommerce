from django.utils.translation import gettext_lazy as _


class AccountMessages:
    LOGIN_SUCCESS = _(" خوش آمدید {username}، ورود شما با موفقیت انجام شد.")
    RATE_LIMIT = _("لطفاً دو دقیقه دیگر دوباره تلاش کنید.")
    SENT_EMAIL = _(
        "اگر حسابی با این ایمیل وجود داشته باشد، لینک بازیابی ارسال خواهد شد."
    )
    INVALID_TOKEN = _("لینک بازیابی رمز عبور معتبر نیست یا منقضی شده است.")
    OLD_PASSWORD = _("رمز عبور جدید همان رمز عبور قدیمی است.")
    PASSWORD_CHANGED = _("رمز عبور با موفقیت تغییر کرد.")
