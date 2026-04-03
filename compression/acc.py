from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID
from agent.state import AgentState
from memory.schemas import BaseMemory
from .summarizers import Summarizer
from .salience import SalienceScorer
from .budgets import BudgetAllocator


class CompressionInput(BaseModel):
    user_message: str
    session_state: AgentState
    retrieved_passages: List[Dict[str, Any]]  # List of passage dicts with text, source, etc.
    memories: List[BaseMemory]
    tool_outputs: List[Dict[str, Any]]  # List of tool output dicts
    policy_rules: Dict[str, Any]  # Policy rules dict


class CompressionOutput(BaseModel):
    compact_active_context: str
    retained_citations: List[Dict[str, Any]]  # Source pointers
    discarded_references: List[Dict[str, Any]]  # Indexed references
    summary_deltas: List[Dict[str, Any]]  # Summary changes


class ACC:
    def __init__(self):
        self.summarizer = Summarizer()
        self.salience_scorer = SalienceScorer()
        self.budget_allocator = BudgetAllocator()

    def compress(self, input_data: CompressionInput) -> CompressionOutput:
        # Orchestrate compression
        # 1. Score salience for all items
        all_items = self._collect_items(input_data)
        salience_scores = self.salience_scorer.score(all_items)

        # 2. Detect novelty and contradictions (basic heuristics)
        novelty_scores = self._detect_novelty(all_items, input_data.session_state)
        contradiction_flags = self._detect_contradictions(all_items)

        # 3. Allocate budgets
        budgets = self.budget_allocator.allocate(input_data.policy_rules)

        # 4. Select items to retain based on scores and budgets
        retained_items = self._select_retained(all_items, salience_scores, novelty_scores, contradiction_flags, budgets)

        # 5. Summarize discarded items
        discarded_items = [item for item in all_items if item not in retained_items]
        discarded_summaries = self.summarizer.summarize_discarded(discarded_items)

        # 6. Build compact context
        compact_context = self._build_compact_context(retained_items, discarded_summaries)

        # 7. Prepare outputs
        retained_citations = [item.get('source', {}) for item in retained_items]
        discarded_references = [{'summary': summary, 'sources': [item.get('source', {}) for item in all_items if item not in retained_items]} for summary in discarded_summaries]
        summary_deltas = []  # Placeholder for deltas

        # 8. Record ACC token savings metrics
        original_token_count = sum(len(item['content'].split()) for item in all_items)
        compact_token_count = len(compact_context.split())
        token_savings = max(0, original_token_count - compact_token_count)

        try:
            from observability.metrics import record_acc_savings
            record_acc_savings(token_savings)
        except Exception:
            pass

        return CompressionOutput(
            compact_active_context=compact_context,
            retained_citations=retained_citations,
            discarded_references=discarded_references,
            summary_deltas=summary_deltas
        )

    def _collect_items(self, input_data: CompressionInput) -> List[Dict[str, Any]]:
        items = []
        # Add user message
        items.append({'type': 'user_message', 'content': input_data.user_message, 'source': {'type': 'user'}})
        # Add retrieved passages
        for passage in input_data.retrieved_passages:
            items.append({'type': 'passage', 'content': passage.get('text', ''), 'source': passage.get('source', {})})
        # Add memories
        for memory in input_data.memories:
            items.append({'type': 'memory', 'content': str(memory.value_json), 'source': {'type': 'memory', 'id': memory.id}})
        # Add tool outputs
        for output in input_data.tool_outputs:
            items.append({'type': 'tool_output', 'content': str(output), 'source': {'type': 'tool'}})
        return items

    def _detect_novelty(self, items: List[Dict[str, Any]], session_state: AgentState) -> List[float]:
        # Basic heuristic: novelty based on presence in recent context
        recent_context = getattr(session_state, 'recent_context', '')
        scores = []
        for item in items:
            if item['content'] in recent_context:
                scores.append(0.5)  # Somewhat novel
            else:
                scores.append(1.0)  # Novel
        return scores

    def _detect_contradictions(self, items: List[Dict[str, Any]]) -> List[bool]:
        # Basic heuristic: flag if content contains contradiction keywords
        flags = []
        for item in items:
            content = item['content'].lower()
            if 'but' in content or 'however' in content or 'contrary' in content:
                flags.append(True)
            else:
                flags.append(False)
        return flags

    def _select_retained(self, items: List[Dict[str, Any]], salience: List[float], novelty: List[float], contradictions: List[bool], budgets: Dict[str, int]) -> List[Dict[str, Any]]:
        retained = []
        type_counts = {'user_message': 0, 'passage': 0, 'memory': 0, 'tool_output': 0}
        for i, item in enumerate(items):
            item_type = item['type']
            if type_counts[item_type] < budgets.get(item_type, 0):
                # Prioritize high salience, high novelty, contradictions
                score = salience[i] * novelty[i]
                if contradictions[i]:
                    score *= 2
                if score > 0.5:  # Threshold
                    retained.append(item)
                    type_counts[item_type] += 1
        return retained

    def _build_compact_context(self, retained_items: List[Dict[str, Any]], discarded_summaries: List[str]) -> str:
        context_parts = []
        for item in retained_items:
            context_parts.append(f"{item['type']}: {item['content']}")
        if discarded_summaries:
            context_parts.append("Discarded summaries: " + "; ".join(discarded_summaries))
        return "\n".join(context_parts)