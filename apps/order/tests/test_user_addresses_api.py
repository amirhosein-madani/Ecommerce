import pytest
from faker import Faker
from django.shortcuts import reverse
from rest_framework.test import APIClient
from accounts.models import User
from order.models.orders import UserAddress

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
def normal_user_address(normal_user):
    return UserAddress.objects.create(
        user=normal_user,
        address_name=fake.word(),
        address=fake.address(),
        state=fake.word(),
        city=fake.city(),
        zip_code=fake.numerify("####"),
    )


@pytest.mark.django_db
class TestUserAddressApi:

    def test_user_address_list_response_200_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_user_address_list_response_401_status(self, api_client):
        url = reverse("order:address-list")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_user_address_list_response_403_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:address-list")
        response = api_client.get(url)
        assert response.status_code == 403

    def test_user_address_create_response_201_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-list")
        data = {
            "user": normal_user,
            "address_name": fake.word(),
            "address": fake.address(),
            "state": fake.word(),
            "city": fake.city(),
            "zip_code": fake.numerify("####"),
        }
        response = api_client.post(url, data)
        assert response.status_code == 201

    def test_user_address_create_response_400_status(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-list")
        data = {}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_user_address_create_response_403_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:address-list")
        data = {
            "user": normal_user,
            "address_name": fake.word(),
            "address": fake.address(),
            "state": fake.word(),
            "city": fake.city(),
            "zip_code": fake.numerify("####"),
        }
        response = api_client.post(url, data)
        assert response.status_code == 403

    def test_user_address_create_response_401_status(self, api_client, normal_user):

        url = reverse("order:address-list")
        data = {
            "user": normal_user,
            "address_name": fake.word(),
            "address": fake.address(),
            "state": fake.word(),
            "city": fake.city(),
            "zip_code": fake.numerify("####"),
        }
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_user_address_detail_response_200_status(
        self, api_client, normal_user, normal_user_address
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_update_user_address_detail_response_200_status(
        self, api_client, normal_user, normal_user_address
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        data = {
            "user": normal_user,
            "address_name": fake.word(),
            "address": fake.address(),
            "state": fake.word(),
            "city": fake.city(),
            "zip_code": fake.numerify("####"),
        }
        response = api_client.put(url, data)
        assert response.status_code == 200

    def test_update_user_address_detail_response_400_status(
        self, api_client, normal_user, normal_user_address
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        data = {}
        response = api_client.put(url, data)
        assert response.status_code == 400

    def test_user_address_detail_nonexistent_pk_response_404_status(
        self, api_client, normal_user
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-detail", kwargs={"pk": 999999})
        response = api_client.get(url)
        assert response.status_code == 404

    def test_delete_user_address_detail_response_204_status(
        self, api_client, normal_user, normal_user_address
    ):
        api_client.force_authenticate(user=normal_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})

        response = api_client.delete(url)
        assert response.status_code == 204

    def test_user_address_detail_response_401_status(
        self, api_client, normal_user_address
    ):
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.get(url)
        assert response.status_code == 401

    def test_update_user_address_detail_response_401_status(
        self, api_client, normal_user_address
    ):
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        data = {
            "address_name": fake.word(),
            "address": fake.address(),
            "state": fake.word(),
            "city": fake.city(),
            "zip_code": fake.numerify("####"),
        }
        response = api_client.put(url, data)
        assert response.status_code == 401

    def test_delete_user_address_detail_response_401_status(
        self, api_client, normal_user_address
    ):
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.delete(url)
        assert response.status_code == 401

    def test_user_address_detail_nonexistent_pk_response_401_status(self, api_client):

        url = reverse("order:address-detail", kwargs={"pk": 999999})
        response = api_client.get(url)
        assert response.status_code == 401

    def test_user_address_detail_response_403_status(
        self, api_client, normal_user_address, admin_user
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.get(url)
        assert response.status_code == 403

    def test_update_user_address_detail_response_403_status(
        self, api_client, normal_user_address, admin_user
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        data = {
            "address_name": fake.word(),
            "address": fake.address(),
            "state": fake.word(),
            "city": fake.city(),
            "zip_code": fake.numerify("####"),
        }
        response = api_client.put(url, data)
        assert response.status_code == 403

    def test_user_address_detail_nonexistent_pk_response_403_status(
        self, api_client, admin_user
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:address-detail", kwargs={"pk": 999999})
        response = api_client.get(url)
        assert response.status_code == 403

    def test_delete_user_address_detail_response_403_status(
        self, api_client, normal_user_address, admin_user
    ):
        api_client.force_authenticate(user=admin_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.delete(url)
        assert response.status_code == 403

    def test_user_cannot_view_another_users_address(
        self, api_client, other_user, normal_user_address
    ):
        api_client.force_authenticate(user=other_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.get(url)
        assert response.status_code == 404

    def test_user_cannot_update_another_users_address(
        self, api_client, other_user, normal_user_address
    ):
        api_client.force_authenticate(user=other_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.put(url, {"address_name": "hacked"})
        assert response.status_code == 404

    def test_user_cannot_delete_another_users_address(
        self, api_client, other_user, normal_user_address
    ):
        api_client.force_authenticate(user=other_user)
        url = reverse("order:address-detail", kwargs={"pk": normal_user_address.pk})
        response = api_client.delete(url)
        assert response.status_code == 404
