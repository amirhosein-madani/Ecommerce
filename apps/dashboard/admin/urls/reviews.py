from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("reviews-list/", views.reviews.ReviewListView.as_view(), name="review_list"),
    path(
        "reviews-update/<int:pk>/",
        views.reviews.ReviewUpdateView.as_view(),
        name="review_edit",
    ),
    path(
        "reviews-delete/<int:pk>/",
        views.reviews.ReviewDeleteView.as_view(),
        name="review_delete",
    ),
]
