import pytest
from django.urls import reverse
from reviews.models import Review, ReviewStatus


@pytest.mark.django_db
class TestReviewAPI:

    def test_admin_review_list_response_401_status(self, api_client):
        url = reverse("reviews:admin-review-list")
        respose = api_client.get(url)
        assert respose.status_code == 401

    def test_admin_review_list_response_200_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-list")
        respose = api_client.get(url)
        assert respose.status_code == 200

    def test_admin_review_list_response_403_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:admin-review-list")
        respose = api_client.get(url)
        assert respose.status_code == 403

    def test_admin_review_create_with_normal_user_response_403_status(
        self, api_client, normal_user
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:admin-review-list")
        data = {}
        respose = api_client.post(url, data)
        assert respose.status_code == 403

    def test_admin_review_create_with_anonymous_user_response_401_status(
        self, api_client, normal_user
    ):
        url = reverse("reviews:admin-review-list")
        data = {}
        respose = api_client.post(url, data)
        assert respose.status_code == 401

    def test_admin_review_create_with_admin_user_response_201_status(
        self, api_client, admin_user, unused_product
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-list")
        data = {
            "product": unused_product.title,
            "description": " eojfoefwfwefwef",
            "rate": 5,
            "status": ReviewStatus.APPROVED,
        }
        respose = api_client.post(url, data)
        assert Review.objects.filter(
            user=admin_user.pk, product=unused_product.pk
        ).exists()
        assert respose.status_code == 201

    def test_admin_review_create_with_admin_user_response_400_status(
        self, api_client, admin_user, unused_product
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-list")
        data = {}
        respose = api_client.post(url, data)
        assert respose.status_code == 400

    def test_admin_review_detail_with_anonymous_user_response_401_status(
        self, api_client, review
    ):
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        respose = api_client.get(url)
        assert respose.status_code == 401

    def test_admin_review_detail_with_normal_user_response_403_status(
        self, api_client, review, normal_user
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        respose = api_client.get(url)
        assert respose.status_code == 403

    def test_admin_review_detail_with_admin_user_response_200_status(
        self, api_client, review, admin_user
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        respose = api_client.get(url)
        assert respose.status_code == 200

    def test_admin_review_update_with_anonymous_user_response_401_status(
        self, api_client, review
    ):
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        data = {}
        respose = api_client.put(url, data)
        assert respose.status_code == 401

    def test_admin_review_update_with_normal_user_response_403_status(
        self, api_client, review, normal_user
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        data = {}
        respose = api_client.put(url, data)
        assert respose.status_code == 403

    def test_admin_update_review_detail_with_admin_user_response_200_status(
        self, api_client, review, admin_user, unused_product
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        data = {
            "product": unused_product.title,
            "description": " eojfoefwfwefwef",
            "rate": 4,
            "status": ReviewStatus.APPROVED,
        }
        respose = api_client.put(url, data)
        assert respose.status_code == 200

    def test_admin_update_review_detail_with_admin_user_response_400_status(
        self, api_client, review, admin_user, unused_product
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        data = {}
        respose = api_client.put(url, data)
        assert respose.status_code == 400

    def test_admin_review_delete_with_anonymous_user_response_401_status(
        self, api_client, review
    ):
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        respose = api_client.delete(url)
        assert respose.status_code == 401

    def test_admin_review_delete_with_normal_user_response_403_status(
        self, api_client, review, normal_user
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        respose = api_client.delete(url)
        assert respose.status_code == 403

    def test_admin_delete_review_with_admin_user_response_204_status(
        self, api_client, review, admin_user
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:admin-review-detail", kwargs={"pk": review.pk})
        respose = api_client.delete(url)
        assert not Review.objects.filter(pk=review.pk).exists()
        assert respose.status_code == 204
