from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from dashboard.permissions import HasCustomerAccessPermission
from products.models import Product
from website.models.wishlists import Wishlist


class WishlistView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    template_name = "dashboard/customer/wishlists/wishlist-list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.object_list.count()
        return context

    def get_queryset(self):
        wishlist = Wishlist.objects.get(user=self.request.user)
        return wishlist.products.select_related().all()


class WishlistRemoveView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.products.remove(product)

        messages.success(request, "محصول از لیست علاقه‌مندی‌ها حذف شد.")

        return redirect(reverse("dashboard:customer:wishlist"))


class WishlistAddView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    def post(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        wishlist = Wishlist.objects.get(user=request.user)

        if wishlist.products.filter(pk=product.pk).exists():
            wishlist.products.remove(product)
            added = False
            message = "محصول از لیست علاقه‌مندی‌ها حذف شد."
        else:
            wishlist.products.add(product)
            added = True
            message = "محصول به لیست علاقه‌مندی‌ها اضافه شد."

        return JsonResponse(
            {
                "message": message,
                "added": added,
            }
        )
