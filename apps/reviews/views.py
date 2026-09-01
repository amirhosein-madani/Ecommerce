from accounts.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView

from products.models import Product, ProductStatusType
from reviews.models import Review
from reviews.forms import ReviewForm
from reviews.messages import ReviewMessages


class SubmitReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    http_method_names = ["post"]

    def form_valid(self, form):
        product = get_object_or_404(
            Product.objects.filter(status=ProductStatusType.PUBLISH),
            slug=self.kwargs["slug"],
        )

        if Review.objects.filter(user=self.request.user, product=product).exists():
            messages.error(self.request, ReviewMessages.ALREADY_EXISTS)
            return redirect(product.get_absolute_url())

        form.instance.user = self.request.user
        form.instance.product = product
        messages.success(self.request, ReviewMessages.SUBMITTED_SUCCESS)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, ReviewMessages.SUBMIT_FAILED)
        return redirect(self.request.META.get("HTTP_REFERER", "/"))

    def get_success_url(self):
        return self.object.product.get_absolute_url()
