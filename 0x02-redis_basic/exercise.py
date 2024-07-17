#!/usr/bin/env python3
"""
Cache module
"""

import redis
import uuid
from typing import Union


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
