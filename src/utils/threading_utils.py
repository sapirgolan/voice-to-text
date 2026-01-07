"""Threading utilities for running tasks asynchronously."""

import threading
from typing import Any, Callable, Optional


def run_in_thread(func: Callable[..., Any], *args: Any, **kwargs: Any) -> threading.Thread:
    """
    Run a function in a separate daemon thread.

    Args:
        func: Function to execute
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Thread object (already started)
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def run_in_thread_with_callback(
    func: Callable[..., Any],
    callback: Optional[Callable[[Any], None]] = None,
    error_callback: Optional[Callable[[Exception], None]] = None,
    *args: Any,
    **kwargs: Any,
) -> threading.Thread:
    """
    Run a function in a separate thread with success and error callbacks.

    Args:
        func: Function to execute
        callback: Called with result if func succeeds
        error_callback: Called with exception if func fails
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Thread object (already started)
    """

    def wrapper() -> None:
        try:
            result = func(*args, **kwargs)
            if callback:
                callback(result)
        except Exception as e:
            if error_callback:
                error_callback(e)
            else:
                print(f"Error in thread: {e}")

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    return thread
