from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DatasetSelection:
    name: str
    input_root: str = ""
    enabled: bool = False
    percentage: float = 0.0
    domain: str = ""


@dataclass(slots=True)
class AppState:
    task: str = "gpt_pretrain"
    target_domain: str = "mixed"
    approximate_token_budget: int = 10_000_000
    dataset_selections: list[DatasetSelection] = field(default_factory=list)
