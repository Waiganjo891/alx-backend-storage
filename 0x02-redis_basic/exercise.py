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


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and
    outputs for a particular function.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method with call history logging.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        inputs_key = f"{method.__qualname__}:inputs"
        outputs_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(inputs_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(outputs_key, str(output))
        return output
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

    @count_calls
    @call_history
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


def replay(method: Callable):
    """
    Displays the history of calls of a particular function.

    Args:
        method (Callable): The function to replay the history of calls.
    """
    cache = method.__self__
    inputs_key = f"{method.__qualname__}:inputs"
    outputs_key = f"{method.__qualname__}:outputs"
    inputs = cache._redis.lrange(inputs_key, 0, -1)
    outputs = cache._redis.lrange(outputs_key, 0, -1)
    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        inp_str = inp.decode('utf-8')
        out_str = out.decode('utf-8')
        print(f"{method.__qualname__}(*{inp_str}) -> {out_str}")


if __name__ == "__main__":
    cache = Cache()
    cache.store("foo")
    cache.store("bar")
    cache.store(42)
    replay(cache.store)
