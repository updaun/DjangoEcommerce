from django.http import HttpRequest
from ninja import Router

from product.response import CategoryListResponse, ProductListResponse
from product.models import Category, Product, ProductStatus
from shared.response import ObjectResponse, response


router = Router(tags=["Products"])


@router.get(
    "",
    response={200: ObjectResponse[ProductListResponse]},
)
def product_list_handler(request: HttpRequest):
    return 200, response(
        ProductListResponse(
            products=Product.objects.filter(status=ProductStatus.ACTIVE).values(
                "id", "name", "price"
            )
        )
    )


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
