class ToolPolicy:
    def is_allowed(self, tool_key: str, allowed_tool_ids: list[str]) -> bool:
        return tool_key in allowed_tool_ids
