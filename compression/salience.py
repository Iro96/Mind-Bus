class SalienceScorer:
    def __init__(self):
        pass

    def score(self, items: list[dict]) -> list[float]:
        scores = []
        for item in items:
            score = self._calculate_salience(item)
            scores.append(score)
        return scores

    def _calculate_salience(self, item: dict) -> float:
        content = item['content']
        item_type = item['type']
        # Heuristics:
        # User messages high salience
        # Tool outputs high if contain results
        # Memories medium
        # Passages low unless contain keywords
        base_score = 0.5
        if item_type == 'user_message':
            base_score = 1.0
        elif item_type == 'tool_output':
            if 'error' in content.lower() or 'result' in content.lower():
                base_score = 0.9
        elif item_type == 'memory':
            base_score = 0.7
        elif item_type == 'passage':
            if any(keyword in content.lower() for keyword in ['important', 'key', 'constraint']):
                base_score = 0.8
        # Length factor: longer items might be more salient
        length_factor = min(1.0, len(content.split()) / 100)
        return base_score * length_factor