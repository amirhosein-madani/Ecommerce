from django.urls import path

from reviews import views

app_name = "reviews"

urlpatterns = [
    path(
        "submit-review/<str:slug>/",
        views.SubmitReviewView.as_view(),
        name="submit_review",
    ),
]
