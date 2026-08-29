from django.urls import path
from .views import NewsletterListApiView, NewsletterRetrieveDestroyAPIView

urlpatterns = [
    path("newsletter-list/", NewsletterListApiView.as_view(), name="newsletter-list"),
    path(
        "newsletter-detail/<int:pk>/",
        NewsletterRetrieveDestroyAPIView.as_view(),
        name="newsletter-detail",
    ),
]
