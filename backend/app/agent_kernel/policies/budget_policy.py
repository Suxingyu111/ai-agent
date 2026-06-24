class BudgetPolicy:
    def within_step_limit(self, current_steps: int, max_steps: int) -> bool:
        return current_steps < max_steps
