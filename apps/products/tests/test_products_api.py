import pytest
from django.shortcuts import reverse

from products.models import ProductStatusType


@pytest.mark.django_db
class TestProductAndCategoryAPI:

    # ==================== LIST ====================

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-list",
            "product:category-list",
        ],
    )
    def test_list_with_admin_user_response_200_status(
        self,
        api_client,
        admin_user,
        url_name,
    ):
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(reverse(url_name))

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-list",
            "product:category-list",
        ],
    )
    def test_list_with_normal_user_response_200_status(
        self,
        api_client,
        normal_user,
        url_name,
    ):
        api_client.force_authenticate(user=normal_user)

        response = api_client.get(reverse(url_name))

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-list",
            "product:category-list",
        ],
    )
    def test_list_with_anonymous_user_response_200_status(
        self,
        api_client,
        url_name,
    ):
        response = api_client.get(reverse(url_name))

        assert response.status_code == 200

    # ==================== DETAIL ====================

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_detail_with_admin_user_response_200_status(
        self,
        api_client,
        admin_user,
        url_name,
        published_product,
        published_category,
    ):
        api_client.force_authenticate(user=admin_user)

        obj = (
            published_product
            if url_name == "product:product-detail"
            else published_category
        )

        response = api_client.get(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_detail_with_normal_user_response_200_status(
        self,
        api_client,
        normal_user,
        url_name,
        published_product,
        published_category,
    ):
        api_client.force_authenticate(user=normal_user)

        obj = (
            published_product
            if url_name == "product:product-detail"
            else published_category
        )

        response = api_client.get(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_detail_with_anonymous_user_response_200_status(
        self,
        api_client,
        url_name,
        published_product,
        published_category,
    ):
        obj = (
            published_product
            if url_name == "product:product-detail"
            else published_category
        )

        response = api_client.get(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 200

    # ==================== INACTIVE DETAIL ====================

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_inactive_detail_with_admin_user_response_200_status(
        self,
        api_client,
        admin_user,
        url_name,
        inactive_product,
        inactive_category,
    ):
        api_client.force_authenticate(user=admin_user)

        obj = (
            inactive_product
            if url_name == "product:product-detail"
            else inactive_category
        )

        response = api_client.get(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_inactive_detail_with_normal_user_response_404_status(
        self,
        api_client,
        normal_user,
        url_name,
        inactive_product,
        inactive_category,
    ):
        api_client.force_authenticate(user=normal_user)

        obj = (
            inactive_product
            if url_name == "product:product-detail"
            else inactive_category
        )

        response = api_client.get(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_inactive_detail_with_anonymous_user_response_404_status(
        self,
        api_client,
        url_name,
        inactive_product,
        inactive_category,
    ):
        obj = (
            inactive_product
            if url_name == "product:product-detail"
            else inactive_category
        )

        response = api_client.get(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 404

    # ==================== DELETE ====================

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_delete_with_admin_user_response_204_status(
        self,
        api_client,
        admin_user,
        url_name,
        published_product,
        published_category,
    ):
        api_client.force_authenticate(user=admin_user)

        obj = (
            published_product
            if url_name == "product:product-detail"
            else published_category
        )

        response = api_client.delete(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 204

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_delete_with_normal_user_response_403_status(
        self,
        api_client,
        normal_user,
        url_name,
        published_product,
        published_category,
    ):
        api_client.force_authenticate(user=normal_user)

        obj = (
            published_product
            if url_name == "product:product-detail"
            else published_category
        )

        response = api_client.delete(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "url_name",
        [
            "product:product-detail",
            "product:category-detail",
        ],
    )
    def test_delete_with_anonymous_user_response_401_status(
        self,
        api_client,
        url_name,
        published_product,
        published_category,
    ):
        obj = (
            published_product
            if url_name == "product:product-detail"
            else published_category
        )

        response = api_client.delete(reverse(url_name, kwargs={"pk": obj.pk}))

        assert response.status_code == 401


@pytest.mark.django_db
class TestProductAPI:

    # ==================== CREATE ====================

    def test_create_product_with_admin_user_response_201_status(
        self,
        api_client,
        admin_user,
    ):
        api_client.force_authenticate(user=admin_user)

        url = reverse("product:product-list")

        data = {
            "title": "wfwefwefwefwef",
            "description": "wfwefwefwefwef",
            "price": 100000000,
            "status": ProductStatusType.PUBLISH,
        }

        response = api_client.post(url, data)

        assert response.status_code == 201

    def test_create_product_with_admin_user_response_400_status(
        self,
        api_client,
        admin_user,
    ):
        api_client.force_authenticate(user=admin_user)

        url = reverse("product:product-list")

        response = api_client.post(url, {})

        assert response.status_code == 400

    def test_create_product_with_normal_user_response_403_status(
        self,
        api_client,
        normal_user,
    ):
        api_client.force_authenticate(user=normal_user)

        url = reverse("product:product-list")

        data = {
            "title": "wfwefwefwefwef",
            "description": "wfwefwefwefwef",
            "price": 100000000,
            "status": ProductStatusType.PUBLISH,
        }

        response = api_client.post(url, data)

        assert response.status_code == 403

    def test_create_product_with_anonymous_user_response_401_status(
        self,
        api_client,
    ):
        url = reverse("product:product-list")

        data = {
            "title": "wfwefwefwefwef",
            "description": "wfwefwefwefwef",
            "price": 100000000,
            "status": ProductStatusType.PUBLISH,
        }

        response = api_client.post(url, data)

        assert response.status_code == 401

    # ==================== UPDATE ====================

    def test_update_product_with_admin_user_response_200_status(
        self,
        api_client,
        admin_user,
        published_product,
    ):
        api_client.force_authenticate(user=admin_user)

        url = reverse(
            "product:product-detail",
            kwargs={"pk": published_product.pk},
        )

        data = {
            "title": "wfwefwefwefwef",
            "description": "wfwefwefwefwef",
            "price": 100000000,
            "status": ProductStatusType.PUBLISH,
        }

        response = api_client.put(url, data)

        assert response.status_code == 200

    def test_update_product_with_admin_user_response_400_status(
        self,
        api_client,
        admin_user,
        published_product,
    ):
        api_client.force_authenticate(user=admin_user)

        url = reverse(
            "product:product-detail",
            kwargs={"pk": published_product.pk},
        )

        response = api_client.put(url, {})

        assert response.status_code == 400

    def test_update_product_with_normal_user_response_403_status(
        self,
        api_client,
        normal_user,
        published_product,
    ):
        api_client.force_authenticate(user=normal_user)

        url = reverse(
            "product:product-detail",
            kwargs={"pk": published_product.pk},
        )

        response = api_client.put(url, {})

        assert response.status_code == 403

    def test_update_product_with_anonymous_user_response_401_status(
        self,
        api_client,
        published_product,
    ):
        url = reverse(
            "product:product-detail",
            kwargs={"pk": published_product.pk},
        )

        response = api_client.put(url, {})

        assert response.status_code == 401


@pytest.mark.django_db
class TestCategoryAPI:

    # ==================== UPDATE ====================

    def test_update_category_with_admin_user_response_200_status(
        self,
        api_client,
        admin_user,
        published_category,
    ):
        api_client.force_authenticate(user=admin_user)

        url = reverse(
            "product:category-detail",
            kwargs={"pk": published_category.pk},
        )

        data = {
            "name": "test",
        }

        response = api_client.put(url, data)

        assert response.status_code == 200

    def test_update_category_with_admin_user_response_400_status(
        self,
        api_client,
        admin_user,
        published_category,
    ):
        api_client.force_authenticate(user=admin_user)

        url = reverse(
            "product:category-detail",
            kwargs={"pk": published_category.pk},
        )

        response = api_client.put(url, {})

        assert response.status_code == 400

    def test_update_category_with_normal_user_response_403_status(
        self,
        api_client,
        normal_user,
        published_category,
    ):
        api_client.force_authenticate(user=normal_user)

        url = reverse(
            "product:category-detail",
            kwargs={"pk": published_category.pk},
        )

        response = api_client.put(url, {})

        assert response.status_code == 403

    def test_update_category_with_anonymous_user_response_401_status(
        self,
        api_client,
        published_category,
    ):
        url = reverse(
            "product:category-detail",
            kwargs={"pk": published_category.pk},
        )

        response = api_client.put(url, {})

        assert response.status_code == 401
