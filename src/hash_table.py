import math

"""
Custom hash table with separate chaining.

This is the CORE data structure for the Mini Shazam project.
You must implement this from scratch — no built-in dicts or hashmaps allowed.

Refer to GUIDE.md, Milestone 1 for detailed instructions.
"""


class HashTable:
    """Hash table using separate chaining.

    Each bucket is a Python list of (key, value) pairs.
    When multiple entries hash to the same bucket, they form a "chain."""

    DEFAULT_CAPACITY = 10007  # A prime number — why prime? See GUIDE.md

    def __init__(self, capacity=None):
        self._capacity = capacity or self.DEFAULT_CAPACITY
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

    # ------------------------------------------------------------------ #
    # Hash function
    # ------------------------------------------------------------------ #

    def _hash(self, key):
        """Map an integer key to a bucket index in range [0, capacity)."""
        key = int(key)
        # Knuth multiplicative hashing constant
        return (key * 2654435761) % self._capacity

    # ------------------------------------------------------------------ #
    # Core operations
    # ------------------------------------------------------------------ #

    def insert(self, key, value):
        """Insert a (key, value) pair into the hash table."""
        index = self._hash(key)
        self._buckets[index].append((key, value))
        self._size += 1

        # Resize when load factor exceeds threshold
        if self.load_factor() > 0.75:
            self._resize()

    def lookup(self, key):
        """Return a list of all values associated with the given key."""
        index = self._hash(key)
        return [v for k, v in self._buckets[index] if k == key]

    # ------------------------------------------------------------------ #
    # Size & statistics
    # ------------------------------------------------------------------ #

    def size(self):
        """Return the total number of stored entries."""
        return self._size

    def capacity(self):
        """Return the current number of buckets."""
        return self._capacity

    def load_factor(self):
        """Return the load factor: entries / capacity."""
        return round(self._size / self._capacity, 4) if self._capacity > 0 else 0.0

    def stats(self):
        """Return collision statistics for the hash table."""
        empty_buckets = sum(1 for bucket in self._buckets if not bucket)
        max_chain_length = max((len(bucket) for bucket in self._buckets), default=0)
        non_empty_buckets = [len(bucket) for bucket in self._buckets if bucket]
        avg_chain_length = (
            round(sum(non_empty_buckets) / len(non_empty_buckets), 4)
            if non_empty_buckets
            else 0.0
        )

        return {
            "capacity": self.capacity(),
            "size": self.size(),
            "load_factor": self.load_factor(),
            "empty_buckets": empty_buckets,
            "max_chain_length": max_chain_length,
            "avg_chain_length": avg_chain_length,
        }

    # ------------------------------------------------------------------ #
    # Resizing
    # ------------------------------------------------------------------ #

    @staticmethod
    def _next_prime(n):
        """
        Find the smallest prime number >= n.

        This is used during resizing: we double the capacity and then
        find the next prime to use as the new capacity. Prime capacities
        help distribute keys more evenly (especially with modular hashing).

        Algorithm:
          1. If n <= 2, return 2
          2. Start with candidate = n (or n+1 if n is even)
          3. Test if candidate is prime by checking divisibility by all odd numbers from 3 to sqrt(candidate)
          4. If not prime, increment by 2 and try again

        Args:
            n: The minimum value for the prime

        Returns:
            The smallest prime >= n
        """
        if n <= 2:
            return 2
        candidate = n if n % 2 != 0 else n + 1
        while True:
            is_prime = True
            for i in range(3, int(math.sqrt(candidate)) + 1, 2):
                if candidate % i == 0:
                    is_prime = False
                    break
            if is_prime:
                return candidate
            candidate += 2

    def _resize(self):
        """
        Double the capacity (to the next prime) and rehash all entries.

        Steps:
          1. Compute new capacity = _next_prime(self._capacity * 2)
          2. Save the old buckets
          3. Reset self._capacity, self._buckets, and self._size
          4. Re-insert every (key, value) pair from the old buckets

        Why is this necessary? As the load factor increases, chains get
        longer and lookups slow down from O(1) toward O(n). Resizing
        keeps chains short.

        What is the time complexity of this operation? How often does it
        happen? What is the amortized cost per insertion? (Think about this!)
        """
        old_buckets = self._buckets
        self._capacity = self._next_prime(self._capacity * 2)
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self.insert(key, value)
        
