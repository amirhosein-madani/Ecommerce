import pytest
from rest_framework.test import APIClient
from accounts.models import User
from products.models import Category, Product, ProductStatusType


@pytest.fixture
def api_client():
    client = APIClient()
    return client


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
def published_product():
    product = Product.objects.create(
        title="test",
        description="mwomweokfmwoiefwoief",
        price=100000000,
        status=ProductStatusType.PUBLISH,
    )
    return product


@pytest.fixture
def inactive_product():
    product = Product.objects.create(
        title="test",
        description="mwomweokfmwoiefwoief",
        price=100000000,
        status=ProductStatusType.DRAFT,
    )
    return product


@pytest.fixture
def published_category():
    category = Category.objects.create(
        name="test",
    )
    return category


@pytest.fixture
def inactive_category():
    category = Category.objects.create(name="test", is_active=False)
    return category
