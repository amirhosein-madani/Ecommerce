from django.contrib.auth import update_session_auth_hash
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from dashboard.permissions import HasCustomerAccessPermission
from dashboard.forms import PasswordChangeForm


class CustomerAddressListView(
    LoginRequiredMixin, HasCustomerAccessPermission, ListView
):

    template_name = "dashboard/customer/addresses/address-list.html"

    def get_queryset(self):
        queryset = UserAddressModel.objects.filter(user=self.request.user)
