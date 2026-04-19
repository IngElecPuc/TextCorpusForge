from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DatasetSelection:
    name: str
    domain: str
    input_root: str = ''
    enabled: bool = False
    percentage: float = 0.0


@dataclass(slots=True)
class AppState:
    task: str = 'seq2seq_mt'
    target_domain: str = 'mixed'
    approximate_token_budget: int = 0
    dataset_selections: list[DatasetSelection] = field(default_factory=list)
