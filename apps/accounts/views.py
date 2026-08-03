from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm
from django.http import Http404
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.cache import cache
from django.views.generic import FormView
from django.utils.encoding import force_str
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from cart.cart import Cart, DBCartAdapter
from products.models import Product
from accounts.forms import PasswordResetRequestForm, ResetPasswordForm
from accounts.tasks import send_reset_password_email
from accounts.messages import AccountMessages

User = get_user_model()


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        session_cart = Cart(self.request.session)
        cart_snapshot = dict(session_cart.cart)

        messages.success(
            self.request,
            AccountMessages.LOGIN_SUCCESS.format(username=form.get_user().username),
        )

        response = super().form_valid(form)

        if cart_snapshot:
            db_cart = DBCartAdapter(self.request.user)

            for product_id, item in cart_snapshot.items():
                product = Product.objects.filter(pk=int(product_id)).first()

                if not product:
                    continue

                current_db_quantity = db_cart.get_quantity(product.pk)
                session_quantity = item["quantity"]
                combined_quantity = current_db_quantity + session_quantity

                allowed_to_add = min(
                    session_quantity, product.stock - current_db_quantity
                )

                if allowed_to_add > 0:
                    db_cart.add(
                        product_id=product.pk,
                        quantity=allowed_to_add,
                        price=item["price"],
                    )

                if combined_quantity > product.stock:
                    messages.warning(
                        self.request,
                        f"تعداد «{product.title}» به‌خاطر محدودیت موجودی به {product.stock} کاهش یافت.",  # noqa:E501
                    )

        return response


def user_logout(request):
    logout(request)
    return redirect("website:index")


class PasswordResetRequestView(FormView):
    template_name = "accounts/reset_password_request.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("request_to_reset_password")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        cache_key = f"password_reset:{email.lower()}"

        if cache.get(cache_key):
            messages.warning(self.request, AccountMessages.RATE_LIMIT)
            return super().form_valid(form)

        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            send_reset_password_email.delay(user.email, user.username, uid, token)

        cache.set(
            cache_key,
            True,
            timeout=120,
        )

        messages.success(self.request, AccountMessages.SENT_EMAIL)

        return super().form_valid(form)


class ResetPasswordView(FormView):
    template_name = "accounts/reset_password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("website:index")

    def dispatch(self, request, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(kwargs["uidb64"]))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise Http404

        if not default_token_generator.check_token(
            self.user,
            kwargs["token"],
        ):
            messages.error(request, AccountMessages.INVALID_TOKEN)
            return redirect("request_to_reset_password")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data["password"]

        if self.user.check_password(password):
            messages.error(self.request, AccountMessages.OLD_PASSWORD)
            return self.form_invalid(form)

        self.user.set_password(password)
        self.user.save(update_fields=["password"])

        messages.success(self.request, AccountMessages.PASSWORD_CHANGED)

        return super().form_valid(form)
