import pytest

from django.shortcuts import reverse

from rest_framework.test import APIClient

from products.models import Product, ProductStatusType


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def common_product():
    return Product.objects.create(
        title="test",
        description="mwomweokfmwoiefwoief",
        price=100000000,
        status=ProductStatusType.PUBLISH,
        stock=13,
    )


@pytest.mark.django_db
class TestCartApi:

    def test_cart_list_response_200_status(self, api_client):
        url = reverse("cart:cart-detail")

        response = api_client.get(url)

        assert response.status_code == 200
        assert "items" in response.data
        assert "total_quantity" in response.data
        assert "total_price" in response.data

    # ---------------------------------------------------------
    # Add to cart
    # ---------------------------------------------------------

    def test_add_item_to_cart_response_200_status(
        self,
        api_client,
        common_product,
    ):
        url = reverse("cart:cart-add")

        data = {
            "product_id": common_product.pk,
            "quantity": 1,
        }

        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["cart_count"] == 1
        assert response.data["total_quantity"] == 1

    def test_add_item_to_cart_response_404_status(
        self,
        api_client,
    ):
        url = reverse("cart:cart-add")

        data = {
            "product_id": 999999,
            "quantity": 1,
        }

        response = api_client.post(url, data)

        assert response.status_code == 404

    def test_add_item_to_cart_response_400_status(
        self,
        api_client,
        common_product,
    ):
        url = reverse("cart:cart-add")

        data = {
            "product_id": common_product.pk,
            "quantity": 999999,
        }

        response = api_client.post(url, data)

        assert response.status_code == 400

    def test_add_item_to_cart_invalid_quantity_response_400_status(
        self,
        api_client,
        common_product,
    ):
        url = reverse("cart:cart-add")

        data = {
            "product_id": common_product.pk,
            "quantity": 0,
        }

        response = api_client.post(url, data)

        assert response.status_code == 400

    # ---------------------------------------------------------
    # Update cart item
    # ---------------------------------------------------------

    def test_update_cart_item_response_200_status(
        self,
        api_client,
        common_product,
    ):
        api_client.post(
            reverse("cart:cart-add"),
            {
                "product_id": common_product.pk,
                "quantity": 1,
            },
        )

        url = reverse(
            "cart:cart-update",
            kwargs={"product_id": common_product.pk},
        )

        response = api_client.patch(
            url,
            {"quantity": 5},
        )

        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["item_total"] == (common_product.final_price * 5)
        assert response.data["total_quantity"] == 5

    def test_update_cart_item_response_404_status(
        self,
        api_client,
    ):
        url = reverse(
            "cart:cart-update",
            kwargs={"product_id": 999999},
        )

        response = api_client.patch(
            url,
            {"quantity": 5},
        )

        assert response.status_code == 404

    def test_update_cart_item_response_400_status(
        self,
        api_client,
        common_product,
    ):
        url = reverse(
            "cart:cart-update",
            kwargs={"product_id": common_product.pk},
        )

        response = api_client.patch(
            url,
            {"quantity": 999999},
        )

        assert response.status_code == 400

    def test_update_cart_item_invalid_quantity_response_400_status(
        self,
        api_client,
        common_product,
    ):
        url = reverse(
            "cart:cart-update",
            kwargs={"product_id": common_product.pk},
        )

        response = api_client.patch(
            url,
            {"quantity": 0},
        )

        assert response.status_code == 400

    # ---------------------------------------------------------
    # Remove cart item
    # ---------------------------------------------------------

    def test_remove_cart_item_response_200_status(
        self,
        api_client,
        common_product,
    ):
        api_client.post(
            reverse("cart:cart-add"),
            {
                "product_id": common_product.pk,
                "quantity": 1,
            },
        )

        url = reverse(
            "cart:cart-remove",
            kwargs={"product_id": common_product.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["total_quantity"] == 0

    def test_remove_cart_item_response_404_status(
        self,
        api_client,
    ):
        url = reverse(
            "cart:cart-remove",
            kwargs={"product_id": 999999},
        )

        response = api_client.delete(url)

        assert response.status_code == 404

    # ---------------------------------------------------------
    # Clear cart
    # ---------------------------------------------------------

    def test_clear_cart_response_200_status(
        self,
        api_client,
    ):
        url = reverse("cart:cart-clear")

        response = api_client.delete(url)

        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["total_quantity"] == 0
