from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

# from django.contrib.messages.views import SuccessMessageMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.forms import PasswordChangeForm
from products.models import Product, Category, ProductStatusType


class ProductListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products/product-list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.with_final_price()

        category_id = self.request.GET.get("category_id")
        search_q = self.request.GET.get("q")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        order_by = self.request.GET.get("order_by")
        is_discounted = self.request.GET.get("is_discounted")

        if is_discounted:
            queryset = queryset.filter(is_discounted=True)

        if order_by:
            queryset = queryset.sort(order_by)

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if search_q:
            queryset = queryset.filter(title__icontains=search_q)

        if min_price:
            queryset = queryset.filter(annotated_final_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(annotated_final_price__lt=max_price)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["total_items"] = context["paginator"].count
        return context
