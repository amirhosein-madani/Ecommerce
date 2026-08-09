from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from dashboard.permissions import HasCustomerAccessPermission
from order.models.orders import UserAddress
from dashboard.customer.forms import UserAddressForm


class CustomerAddressListView(
    LoginRequiredMixin, HasCustomerAccessPermission, ListView
):

    template_name = "dashboard/customer/addresses/address-list.html"

    def get_queryset(self):
        queryset = UserAddress.objects.filter(user=self.request.user)
        return queryset


class CustomerAddressCreateView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    SuccessMessageMixin,
    CreateView,
):
    model = UserAddress
    form_class = UserAddressForm
    template_name = "dashboard/customer/addresses/address-create.html"
    success_url = reverse_lazy("dashboard:customer:address_list")
    success_message = _("آدرس با موفقیت اضافه شد ")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CustomerAddressEditView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    model = UserAddress
    form_class = UserAddressForm
    template_name = "dashboard/customer/addresses/address-edit.html"
    success_url = reverse_lazy("dashboard:customer:address_list")
    success_message = _("آدرس با موفقیت ویرایش شد ")

    def get_queryset(self):
        queryset = UserAddress.objects.filter(user=self.request.user)
        return queryset


class CustomerAddressDeleteView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    model = UserAddress
    template_name = "dashboard/customer/addresses/address-delete.html"
    success_url = reverse_lazy("dashboard:customer:address_list")
    success_message = _("آدرس با موفقیت حذف شد ")

    def get_queryset(self):
        queryset = UserAddress.objects.filter(user=self.request.user)
        return queryset
