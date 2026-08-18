import pytest
from faker import Faker
from django.shortcuts import reverse
from rest_framework.test import APIClient
from accounts.models import User
from order.models.coupons import Coupon

fake = Faker()


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def other_user():
    return User.objects.create_user(
        username="other",
        password="amirmad2007",
        email="other@gmail.com",
        national_code="9420100111",
    )


@pytest.fixture
def admin_user():
    user = User.objects.create_superuser(
        username="amir",
        password="amirmad2007",
        email="amirmadani901@gmail.com",
        national_code="6300110117",
    )
    return user


@pytest.fixture
def normal_user():
    user = User.objects.create_user(
        username="normal",
        password="amirmad2007",
        email="example@gmail.com",
        national_code="0250704961",
    )
    return user


@pytest.fixture
def coupon():
    coupon = Coupon.objects.create(
        code=fake.word(),
        discount=20,
        minimum_order_price=4000,
        max_discount=400000,
    )
    return coupon


@pytest.mark.django_db
class TestCouponApi:

    def test_coupon_list_response_200_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:coupon-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_coupon_list_response_401_status(self, api_client):
        url = reverse("order:coupon-list")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_coupon_list_response_403_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:coupon-list")
        response = api_client.get(url)
        assert response.status_code == 403

    def test_create_coupon_response_201_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-list")
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert Coupon.objects.filter(code=data["code"]).exists()

    def test_create_coupon_response_400_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        data = {}
        url = reverse("order:coupon-list")
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_create_coupon_response_401_status(self, api_client):
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-list")
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_create_coupon_response_403_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-list")
        response = api_client.post(url, data)
        assert response.status_code == 403

    def test_create_coupon_with_duplicate_code_response_400_status(
        self, api_client, admin_user, coupon
    ):
        api_client.force_authenticate(user=admin_user)
        data = {
            "code": coupon.code,
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-list")
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_coupon_detail_response_200_status(self, api_client, admin_user, coupon):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_coupon_detail_response_401_status(self, api_client, coupon):
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.get(url)
        assert response.status_code == 401

    def test_coupon_detail_response_403_status(self, api_client, normal_user, coupon):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.get(url)
        assert response.status_code == 403

    def test_coupon_detail_response_404_status(self, api_client, admin_user, coupon):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:coupon-detail", kwargs={"pk": 99999999})
        response = api_client.get(url)
        assert response.status_code == 404

    def test_update_coupon_detail_response_200_status(
        self, api_client, admin_user, coupon
    ):
        api_client.force_authenticate(user=admin_user)
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.put(url, data)
        assert response.status_code == 200
        assert Coupon.objects.get(pk=coupon.pk).discount == 20

    def test_update_coupon_detail_with_normal_user_response_403_status(
        self, api_client, normal_user, coupon
    ):
        api_client.force_authenticate(user=normal_user)
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.put(url, data)
        assert response.status_code == 403

    def test_update_coupon_detail_with_anonymous_user_response_401_status(
        self, api_client, coupon
    ):
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.put(url, data)
        assert response.status_code == 401

    def test_update_coupon_detail_response_400_status(
        self, api_client, admin_user, coupon
    ):
        api_client.force_authenticate(user=admin_user)
        data = {}
        url = reverse("order:coupon-detail", kwargs={"pk": coupon.pk})
        response = api_client.put(url, data)
        assert response.status_code == 400

    def test_update_coupon_detail_response_404_status(
        self, api_client, admin_user, coupon
    ):
        api_client.force_authenticate(user=admin_user)
        data = {
            "code": fake.word(),
            "discount": 20,
            "minimum_order_price": 4000,
            "max_discount": 400000,
        }
        url = reverse("order:coupon-detail", kwargs={"pk": 999999999})
        response = api_client.put(url, data)
        assert response.status_code == 404

    def test_delete_coupon_detail_response_204_status(
        self, api_client, admin_user, coupon
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse(
            "order:coupon-detail",
            kwargs={"pk": coupon.pk},
        )
        response = api_client.delete(url)
        assert response.status_code == 204
        assert not Coupon.objects.filter(pk=coupon.pk).exists()

    def test_delete_coupon_detail_response_401_status(self, api_client, coupon):
        url = reverse(
            "order:coupon-detail",
            kwargs={"pk": coupon.pk},
        )
        response = api_client.delete(url)

        assert response.status_code == 401

    def test_delete_coupon_detail_response_403_status(
        self, api_client, normal_user, coupon
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse(
            "order:coupon-detail",
            kwargs={"pk": coupon.pk},
        )
        response = api_client.delete(url)
        assert response.status_code == 403

    def test_delete_coupon_detail_response_404_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse(
            "order:coupon-detail",
            kwargs={"pk": 99999999},
        )
        response = api_client.delete(url)
        assert response.status_code == 404
