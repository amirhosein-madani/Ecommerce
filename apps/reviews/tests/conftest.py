import pytest
from rest_framework.test import APIClient
from accounts.models import User
from reviews.models import ReviewStatus, Review
from products.models import Product, ProductStatusType


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
        stock=10,
    )
    return product


@pytest.fixture
def unused_product():
    product = Product.objects.create(
        title="efefef",
        description="wwefwefwfwef",
        price=100000000,
        status=ProductStatusType.PUBLISH,
        stock=10,
    )
    return product


@pytest.fixture
def review(normal_user, published_product):
    return Review.objects.create(
        user=normal_user,
        product=published_product,
        description="Test review",
        rate=5,
        status=ReviewStatus.PENDING,
    )
