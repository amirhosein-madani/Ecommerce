from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from dashboard.admin.forms import CouponForm
from dashboard.permissions import HasAdminAccessPermission
from order.models.coupons import Coupon


class CouponListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView,
):
    model = Coupon
    template_name = "dashboard/admin/coupons/coupon-list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Coupon.objects.all()

        search_q = self.request.GET.get("q")
        order_by = self.request.GET.get("order_by")

        if search_q:
            queryset = queryset.filter(code__icontains=search_q)

        if order_by in ["created_at", "-created_at"]:
            queryset = queryset.order_by(order_by)

        return queryset


class CouponCreateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    CreateView,
):
    model = Coupon
    form_class = CouponForm
    template_name = "dashboard/admin/coupons/coupon-create.html"
    success_url = reverse_lazy("dashboard:admin:coupon_list")
    success_message = "کد تخفیف با موفقیت ساخته شد."


class CouponUpdateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    model = Coupon
    form_class = CouponForm
    template_name = "dashboard/admin/coupons/coupon-edit.html"
    success_message = "کد تخفیف با موفقیت تغییر کرد."

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:coupon_update",
            kwargs={"pk": self.object.pk},
        )


class CouponDeleteView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    model = Coupon
    template_name = "dashboard/admin/coupons/coupon-delete.html"
    success_url = reverse_lazy("dashboard:admin:coupon_list")
    success_message = "کد تخفیف با موفقیت حذف شد."
