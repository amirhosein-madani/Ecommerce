from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("coupon-list/", views.coupons.CouponListView.as_view(), name="coupon_list"),
    path(
        "coupon-update/<int:pk>/",
        views.coupons.CouponUpdateView.as_view(),
        name="coupon_update",
    ),
    path(
        "coupon-delete/<int:pk>/",
        views.coupons.CouponDeleteView.as_view(),
        name="coupon_delete",
    ),
    path(
        "create-coupon/",
        views.coupons.CouponCreateView.as_view(),
        name="coupon_create",
    ),
]
