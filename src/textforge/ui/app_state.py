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
    max_pairs: int = 0
    max_segments: int = 0
    max_documents: int = 0
    max_tokens_approx: int = 0
    sample_export_size: int = 20
    mode_preview_only: bool = False
    stop_after_first_dataset: bool = True
    export_samples: bool = True
    dataset_selections: list[DatasetSelection] = field(default_factory=list)
