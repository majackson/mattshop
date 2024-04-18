class OrderError(Exception):
    """A general exception raised when an error occurs during the order process."""
    pass

class OutOfStockOrderError(OrderError):
    """Raised when an order fails due to an item being out of stock."""
    pass