#!/usr/bin/env python3
"""
Cache module
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of calls to a method.
    Args:
        method (Callable): The method to be decorated.
    Returns:
        Callable: The wrapped method with call counting.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """
    A Cache class to interact with a Redis database.
    Attributes:
        _redis (redis.Redis): Instance of Redis client.
    """
    def __init__(self):
        """
        Initializes the Cache class and flushes the Redis database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in Redis with a randomly generated key.
        Args:
            data (Union[str, bytes, int, float]): Data to store in Redis.
        Returns:
            str: The generated key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self, key: str, fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float, None]:
        """
        Retrieves data from Redis and applies an optional conversion function.
        Args:
            key (str): The key under which the data is stored.
            fn (Optional[Callable]): A callable to convert the data.
        Returns:
            Union[str, bytes, int, float, None]: The retrieved data or
            None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieves a string from Redis.
        Args:
            key (str): The key under which the data is stored.
        Returns:
            Optional[str]: The retrieved string or None if
            the key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieves an integer from Redis.
        Args:
            key (str): The key under which the data is stored.
        Returns:
            Optional[int]: The retrieved integer or None if the
            key does not exist.
        """
        return self.get(key, fn=int)


if __name__ == "__main__":
    cache = Cache()
    TEST_CASES = {
        b"foo": None,
        123: int,
        "bar": lambda d: d.decode("utf-8")
    }
    for value, fn in TEST_CASES.items():
        key = cache.store(value)
        assert cache.get(key, fn=fn) == value
    cache.store(b"first")
    print(cache.get(cache.store.__qualname__))
    cache.store(b"second")
    cache.store(b"third")
    print(cache.get(cache.store.__qualname__))
