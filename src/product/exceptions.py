class OrderInvalidProductException(Exception):
    message = "Invalid product id"


class OrderNotFoundException(Exception):
    message = "Order not found"


class OrderPaymentConfirmFailedException(Exception):
    message = "Order payment confirmation failed"


class OrderAlreadyPaidException(Exception):
    message = "Order already paid"
