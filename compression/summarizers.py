class Summarizer:
    def __init__(self):
        pass

    def summarize_discarded(self, discarded_items: list) -> list[str]:
        # Basic summarization: group by type and summarize
        summaries = []
        type_groups = {}
        for item in discarded_items:
            item_type = item['type']
            if item_type not in type_groups:
                type_groups[item_type] = []
            type_groups[item_type].append(item['content'])

        for item_type, contents in type_groups.items():
            if len(contents) > 1:
                summary = f"{item_type}: {len(contents)} items discarded, key points: {self._extract_key_points(contents)}"
            else:
                summary = f"{item_type}: {contents[0][:50]}..."
            summaries.append(summary)
        return summaries

    def _extract_key_points(self, contents: list[str]) -> str:
        # Simple heuristic: take first few words from each
        points = []
        for content in contents[:3]:  # Limit to 3
            words = content.split()[:5]
            points.append(" ".join(words))
        return ", ".join(points)