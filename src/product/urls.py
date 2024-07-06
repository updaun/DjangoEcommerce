from typing import List
from django.http import HttpRequest
from ninja import Router

from product.response import CategoryListResponse, ProductListResponse
from product.models import Category, Product, ProductStatus
from shared.response import ObjectResponse, response

from user.authentication import bearer_auth, AuthRequest
from shared.response import ErrorResponse

from django.db import transaction
from product.models import Order, OrderLine, OrderStatus
from product.request import OrderRequestBody
from product.response import OrderDetailResponse, OkResponse
from shared.response import error_response
from product.exceptions import (
    OrderInvalidProductException,
    OrderNotFoundException,
    OrderAlreadyPaidException,
    UserPointsNotEnoughException,
    UserVersionConflictException,
)

from typing import Dict
from user.models import ServiceUser, UserPointsHistory
from django.db import models


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


@router.post(
    "/orders/{order_id}/confirm",
    response={
        200: ObjectResponse[OkResponse],
        400: ObjectResponse[ErrorResponse],
        404: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def confirm_order_payment_handler(request: AuthRequest, order_id: int):
    if not (order := Order.objects.filter(id=order_id, user=request.user).first()):
        return 404, error_response(msg=OrderNotFoundException.message)

    # if not payment_service.confirm_payment(
    #     payment_key=body.payment_key, amount=order.total_price
    # ):
    #     return 400, error_response(msg=OrderPaymentConfirmFailedException.message)

    with transaction.atomic():
        success: int = Order.objects.filter(
            id=order_id, status=OrderStatus.PENDING
        ).update(status=OrderStatus.PAID)
        if not success:
            return 400, error_response(msg=OrderAlreadyPaidException.message)

        user = ServiceUser.objects.select_for_update().get(id=request.user.id)
        if user.points < order.total_price:
            return 409, error_response(msg=UserPointsNotEnoughException.message)

        # order count and use points
        # ServiceUser.objects.filter(id=request.user.id).update(
        #     points=models.F("points") - order.total_price,
        #     order_count=models.F("order_count") + 1,
        # )

        # order count and use points
        success: int = ServiceUser.objects.filter(
            id=request.user.id, version=user.version
        ).update(
            points=models.F("points") - order.total_price,
            order_count=models.F("order_count") + 1,
            version=user.version + 1,
        )
        if not success:
            return 409, error_response(msg=UserVersionConflictException.message)

        UserPointsHistory.objects.create(
            user=user,
            points_change=-order.total_price,
            reason=f"orders:{order.id}:confirm",
        )

    # send email
    return 200, response(OkResponse())
