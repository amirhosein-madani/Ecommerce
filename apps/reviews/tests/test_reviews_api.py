import pytest
from django.urls import reverse
from reviews.models import Review


@pytest.mark.django_db
class TestReviewAPI:

    def test_review_list_response_200_status(self, api_client):
        url = reverse("reviews:review-list-create")
        respose = api_client.get(url)
        assert respose.status_code == 200

    def test_review_create_response_401_status(self, api_client):
        url = reverse("reviews:review-list-create")
        data = {}
        respose = api_client.post(url, data)
        assert respose.status_code == 401

    def test_review_create_response_201_status(
        self, api_client, normal_user, unused_product
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:review-list-create")
        data = {
            "product": unused_product.title,
            "description": " eojfoefwfwefwef",
            "rate": 5,
        }
        respose = api_client.post(url, data)
        assert Review.objects.filter(
            user=normal_user.pk, product=unused_product.pk
        ).exists()
        assert respose.status_code == 201

    def test_review_create_response_400_status(
        self, api_client, normal_user, unused_product
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:review-list-create")
        data = {}
        respose = api_client.post(url, data)
        assert respose.status_code == 400

    def test_create_duplicate_review_response_400_status(
        self, api_client, normal_user, published_product, review
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:review-list-create")
        data = {
            "product": published_product.title,
            "description": " eojfoefwfwefwef",
            "rate": 5,
        }
        respose = api_client.post(url, data)
        assert respose.status_code == 400

    def test_review_detail_response_401_status(self, api_client, review):
        url = reverse("reviews:review-retrieve-destroy", kwargs={"pk": review.pk})
        respose = api_client.get(url)
        assert respose.status_code == 401

    def test_review_detail_response_200_status(self, api_client, review, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:review-retrieve-destroy", kwargs={"pk": review.pk})
        respose = api_client.get(url)
        assert respose.status_code == 200

    def test_review_detail_response_403_status(self, api_client, review, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:review-retrieve-destroy", kwargs={"pk": review.pk})
        respose = api_client.get(url)
        assert respose.status_code == 404

    def test_review_delete_response_401_status(self, api_client, review):
        url = reverse("reviews:review-retrieve-destroy", kwargs={"pk": review.pk})
        respose = api_client.delete(url)
        assert respose.status_code == 401

    def test_review_delete_response_204_status(self, api_client, review, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:review-retrieve-destroy", kwargs={"pk": review.pk})
        respose = api_client.delete(url)
        assert not Review.objects.filter(user=normal_user.pk, pk=review.pk).exists()
        assert respose.status_code == 204

    def test_review_delete_response_404_status(self, api_client, review, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:review-retrieve-destroy", kwargs={"pk": review.pk})
        respose = api_client.delete(url)
        assert respose.status_code == 404

    def test_customer_review_list_response_200_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("reviews:customer-review-list")
        respose = api_client.get(url)
        assert respose.status_code == 200

    def test_customer_review_list_response_403_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("reviews:customer-review-list")
        respose = api_client.get(url)
        assert respose.status_code == 403

    def test_customer_review_list_response_401_status(self, api_client):
        url = reverse("reviews:customer-review-list")
        respose = api_client.get(url)
        assert respose.status_code == 401
