from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path(
        "new-letters/",
        views.newletters.NewsLetterListView.as_view(),
        name="newsletter_list",
    ),
    path(
        "new-letters/delete/<int:pk>/",
        views.newletters.NewsLetterDeleteieView.as_view(),
        name="newsletter_delete",
    ),
]
