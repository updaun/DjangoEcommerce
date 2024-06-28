import pytest

from product.models import Product, ProductStatus
from schema import Schema

from user.models import ServiceUser
from user.authentication import authentication_service

from product.models import OrderLine


@pytest.mark.django_db
def test_get_product_list(api_client):
    # given
    Product.objects.create(name="청바지", price=1, status="active")

    # when
    response = api_client.get("/products")

    # then
    assert response.status_code == 200
    assert len(response.json()["results"]["products"]) == 1
    assert Schema(
        {"results": {"products": [{"id": int, "name": "청바지", "price": 1}]}}
    ).validate(response.json())


@pytest.mark.django_db
def test_order_products(api_client):
    user = ServiceUser.objects.create(email="goodpang@example.com")
    token = authentication_service.encode_token(user_id=user.id)

    p1 = Product.objects.create(name="청바지", price=1000, status=ProductStatus.ACTIVE)
    p2 = Product.objects.create(name="티셔츠", price=500, status=ProductStatus.ACTIVE)

    response = api_client.post(
        "/products/orders",
        data={
            "order_lines": [
                {"product_id": p1.id, "quantity": 2},
                {"product_id": p2.id, "quantity": 3},
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert Schema(
        {
            "results": {
                "id": int,
                "total_price": int((p1.price * 2 * 0.9) + (p2.price * 3 * 0.9)),
            }
        }
    ).validate(response.json())

    order_id = response.json()["results"]["id"]
    assert OrderLine.objects.filter(order_id=order_id).count() == 2
