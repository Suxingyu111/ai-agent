class MemoryPolicy:
    def can_access_namespace(self, requested_namespace: str, own_namespace: str) -> bool:
        return requested_namespace == own_namespace
