class KnowledgePolicy:
    def can_access_scope(self, scope_id: str, allowed_scope_ids: list[str]) -> bool:
        return scope_id in allowed_scope_ids
