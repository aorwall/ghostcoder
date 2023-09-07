class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.usage_order = []

    def put(self, key, value):
        if key in self.cache:
            self.usage_order.remove(key)
        elif len(self.cache) == self.capacity:
            evicted_key = self.usage_order.pop(0)
            del self.cache[evicted_key]

        self.cache[key] = value
        self.usage_order.append(key)

    def get(self, key):
        if key not in self.cache:
            return None

        self.usage_order.remove(key)
        self.usage_order.append(key)
        return self.cache[key]
