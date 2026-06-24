class SafetyPolicy:
    def requires_approval(self, action_key: str, approval_required_actions: list[str]) -> bool:
        return action_key in approval_required_actions
