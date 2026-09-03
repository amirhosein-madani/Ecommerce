from django.urls import path

from dashboard.customer import views

urlpatterns = [
    path("reviews-list/", views.reviews.ReviewListView.as_view(), name="review_list"),
    path(
        "reviews-detail/<int:pk>/",
        views.reviews.ReviewDetailView.as_view(),
        name="review_detail",
    ),
]
