class BudgetAllocator:
    def __init__(self):
        self.default_budgets = {
            'user_message': 1,  # Always keep user message
            'passage': 5,
            'memory': 3,
            'tool_output': 2
        }

    def allocate(self, policy_rules: dict) -> dict[str, int]:
        budgets = self.default_budgets.copy()
        # Adjust based on policy rules
        if 'max_passages' in policy_rules:
            budgets['passage'] = policy_rules['max_passages']
        if 'max_memories' in policy_rules:
            budgets['memory'] = policy_rules['max_memories']
        # Token-based budgets, but for now, count-based
        return budgets