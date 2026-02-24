class CartServiceException(Exception):
    """Базовое исключение Cart Service."""

    detail = "Cart service internal error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundException(CartServiceException):
    detail = "Resource not found"


class ServiceUnavailableException(CartServiceException):
    detail = "External service is temporarily unavailable"
