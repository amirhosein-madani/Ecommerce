from django.urls import path

from dashboard.customer import views

urlpatterns = [
    path("wishlist/", views.wishlists.WishlistView.as_view(), name="wishlist"),
    path(
        "wishlist-remove/<int:pk>",
        views.wishlists.WishlistRemoveView.as_view(),
        name="wishlist_remove",
    ),
    path(
        "wishlist-add/<int:pk>",
        views.wishlists.WishlistAddView.as_view(),
        name="wishlist_add",
    ),
]
