from typing import List
from django.http import HttpRequest
from ninja import Router

from product.response import CategoryListResponse, ProductListResponse
from product.models import Category, Product, ProductStatus
from shared.response import ObjectResponse, response

from user.authentication import bearer_auth, AuthRequest
from shared.response import ErrorResponse

from django.db import transaction
from product.models import Order, OrderLine
from product.request import OrderRequestBody
from product.response import OrderDetailResponse
from shared.response import error_response
from product.exceptions import OrderInvalidProductException

from typing import Dict


router = Router(tags=["Products"])


@router.get(
    "",
    response={200: ObjectResponse[ProductListResponse]},
)
def product_list_handler(
    request: HttpRequest, category_id: int | None = None, query: str | None = None
):
    if query:
        # products = Product.objects.filter(
        #     search_vector=SearchQuery(query), status=ProductStatus.ACTIVE
        # ).values("id", "name", "price")
        products = Product.objects.filter(name__contains=query)[100:]
    elif category_id:
        category: Category | None = Category.objects.filter(id=category_id).first()
        if not category:
            products = []
        else:
            category_ids: List[int] = [category.id] + list(
                category.children.values_list("id", flat=True)
            )
            products = Product.objects.filter(
                category_id__in=category_ids, status=ProductStatus.ACTIVE
            ).values("id", "name", "price")
    else:
        products = Product.objects.filter(status=ProductStatus.ACTIVE).values(
            "id", "name", "price"
        )
    return 200, response(ProductListResponse(products=products))


@router.get(
    "/categories",
    response={
        200: ObjectResponse[CategoryListResponse],
    },
)
def categories_list_handler(request: HttpRequest):
    return 200, response(
        CategoryListResponse.build(
            categories=Category.objects.filter(parent=None).prefetch_related("children")
        )
    )


@router.post(
    "/orders",
    response={
        201: ObjectResponse[OrderDetailResponse],
        400: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def order_products_handler(request: AuthRequest, body: OrderRequestBody):
    product_id_to_quantity: Dict[int, int] = body.product_id_to_quantity
    products: List[Product] = list(
        Product.objects.filter(id__in=product_id_to_quantity)
    )
    if len(products) != len(product_id_to_quantity):
        return 400, error_response(msg=OrderInvalidProductException.message)

    with transaction.atomic():
        total_price: int = 0
        order = Order.objects.create(user=request.user, total_price=total_price)

        order_lines_to_create: List[OrderLine] = []
        for product in products:
            price: int = product.price
            discount_ratio: float = 0.9
            quantity: int = product_id_to_quantity[product.id]

            order_lines_to_create.append(
                OrderLine(
                    product=product,
                    order=order,
                    quantity=quantity,
                    price=price,
                    discount_ratio=discount_ratio,
                )
            )

            total_price += product.price * quantity * discount_ratio

        order.total_price = int(total_price)
        order.save()
        OrderLine.objects.bulk_create(order_lines_to_create)

    return 201, response({"id": order.id, "total_price": order.total_price})
