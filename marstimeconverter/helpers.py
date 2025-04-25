import warnings
from functools import wraps

def deprecated(new_name):
    """
    Decorator to mark functions as deprecated.
    Issues a DeprecationWarning when the function is used.

    :param new_name: The name of the new function that should be used.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated and will be removed in a future version. "
                f"Please use {new_name} instead.",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator