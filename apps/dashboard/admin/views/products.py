from django.views.generic import (
    UpdateView,
    ListView,
    DeleteView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import ProductUpdateForm
from products.models import Product, Category


class ProductListView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, ListView
):
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


class ProductUpdateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = Product
    form_class = ProductUpdateForm
    template_name = "dashboard/admin/products/product-edit.html"
    success_message = _(" محصول با موفقیت تغییر کرد")

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product_update", kwargs={"pk": self.get_object().pk}
        )


# class ProductImageEditView(LoginRequiredMixin, HasAdminAccessPermission, View):

#     def post(self, request, pk, *args, **kwargs):

#         product = get_object_or_404(Product, pk=pk)

#         form = ProductImageForm(request.POST, request.FILES, instance=product)

#         if form.is_valid():
#             form.save()
#             messages.success(request, _("تصویر محصول با موفقیت به‌روزرسانی شد"))
#         else:
#             messages.error(request, _("فایل انتخاب‌شده معتبر نیست"))

#         return redirect("dashboard:admin:product_list")


class ProductDeleteView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView
):
    model = Product
    template_name = "dashboard/admin/products/product-delete.html"
    success_url = reverse_lazy("dashboard:admin:product_list")
    success_message = _(" محصول با موفقیت حذف شد")


class ProductCreateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView
):
    model = Product
    form_class = ProductUpdateForm
    template_name = "dashboard/admin/products/product-create.html"
    success_url = reverse_lazy("dashboard:admin:product_list")
    success_message = _(" محصول با موفقیت ساخته شد")
