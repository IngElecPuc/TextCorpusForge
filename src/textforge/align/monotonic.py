from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class AlignmentCandidate:
    src_indices: tuple[int, ...]
    tgt_indices: tuple[int, ...]
    score: float
    alignment_type: str
    quality_flags: list[str]


@dataclass(slots=True)
class TextUnit:
    index: int
    text_raw: str
    text_norm: str
    sequence_index: int
    line_numbers: tuple[int, ...]

    @property
    def char_len(self) -> int:
        return len(self.text_norm)

    @property
    def word_len(self) -> int:
        return len(self.text_norm.split())


_ALLOWED_MOVES: tuple[tuple[int, int], ...] = (
    (1, 1),
    (1, 2),
    (2, 1),
    (1, 0),
    (0, 1),
)


def monotonic_align(
    src_units: Sequence[TextUnit],
    tgt_units: Sequence[TextUnit],
    *,
    max_merge_src: int = 2,
    max_merge_tgt: int = 2,
    skip_penalty: float = 2.4,
    mismatch_penalty: float = 5.0,
    alignment_type: str = "monotonic_windowed",
) -> list[AlignmentCandidate]:
    if not src_units and not tgt_units:
        return []
    n = len(src_units)
    m = len(tgt_units)
    inf = float("inf")
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    back: list[list[tuple[int, int] | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    for i in range(n + 1):
        for j in range(m + 1):
            current = dp[i][j]
            if math.isinf(current):
                continue
            for take_src, take_tgt in _ALLOWED_MOVES:
                if take_src > max_merge_src or take_tgt > max_merge_tgt:
                    continue
                ni = i + take_src
                nj = j + take_tgt
                if ni > n or nj > m or (take_src == 0 and take_tgt == 0):
                    continue
                extra = _transition_cost(src_units[i:ni], tgt_units[j:nj], skip_penalty=skip_penalty, mismatch_penalty=mismatch_penalty)
                candidate = current + extra
                if candidate < dp[ni][nj]:
                    dp[ni][nj] = candidate
                    back[ni][nj] = (take_src, take_tgt)

    if math.isinf(dp[n][m]):
        return []

    raw_steps: list[tuple[int, int, int, int]] = []
    i, j = n, m
    while i > 0 or j > 0:
        move = back[i][j]
        if move is None:
            break
        take_src, take_tgt = move
        raw_steps.append((i - take_src, i, j - take_tgt, j))
        i -= take_src
        j -= take_tgt
    raw_steps.reverse()

    aligned: list[AlignmentCandidate] = []
    for src_start, src_end, tgt_start, tgt_end in raw_steps:
        src_slice = src_units[src_start:src_end]
        tgt_slice = tgt_units[tgt_start:tgt_end]
        score = _transition_cost(src_slice, tgt_slice, skip_penalty=skip_penalty, mismatch_penalty=mismatch_penalty)
        flags: list[str] = []
        if not src_slice:
            flags.append("src_gap")
        if not tgt_slice:
            flags.append("tgt_gap")
        if len(src_slice) != 1 or len(tgt_slice) != 1:
            flags.append("merged_alignment")
        if _digit_count(_join_norm(src_slice)) != _digit_count(_join_norm(tgt_slice)):
            flags.append("digit_mismatch")
        aligned.append(
            AlignmentCandidate(
                src_indices=tuple(unit.index for unit in src_slice),
                tgt_indices=tuple(unit.index for unit in tgt_slice),
                score=score,
                alignment_type=alignment_type,
                quality_flags=flags,
            )
        )
    return aligned


def _transition_cost(
    src_slice: Sequence[TextUnit],
    tgt_slice: Sequence[TextUnit],
    *,
    skip_penalty: float,
    mismatch_penalty: float,
) -> float:
    if not src_slice and not tgt_slice:
        return 0.0
    if not src_slice or not tgt_slice:
        size = len(src_slice) or len(tgt_slice)
        text = _join_norm(src_slice or tgt_slice)
        penalty = skip_penalty + (0.15 * len(text.split())) + (0.01 * len(text))
        return penalty + (0.35 * max(size - 1, 0))

    src_text = _join_norm(src_slice)
    tgt_text = _join_norm(tgt_slice)
    src_len = max(len(src_text), 1)
    tgt_len = max(len(tgt_text), 1)

    ratio_cost = abs(math.log(src_len / tgt_len))
    punctuation_cost = 0.15 * abs(_punctuation_count(src_text) - _punctuation_count(tgt_text))
    digit_cost = 0.5 * abs(_digit_count(src_text) - _digit_count(tgt_text))
    quote_cost = 0.3 if _quote_profile(src_text) != _quote_profile(tgt_text) else 0.0
    speaker_cost = 0.45 if _speaker_marker(src_text) != _speaker_marker(tgt_text) else 0.0
    merge_cost = 0.2 * (max(len(src_slice), len(tgt_slice)) - 1)

    total = ratio_cost + punctuation_cost + digit_cost + quote_cost + speaker_cost + merge_cost
    if ratio_cost > 1.6:
        total += mismatch_penalty
    return total


def _join_norm(units: Sequence[TextUnit]) -> str:
    return " ".join(unit.text_norm for unit in units if unit.text_norm).strip()


def _punctuation_count(text: str) -> int:
    return sum(1 for ch in text if ch in ".,;:!?¿¡()[]\"'“”‘’«»—-")


def _digit_count(text: str) -> int:
    return sum(1 for ch in text if ch.isdigit())


def _quote_profile(text: str) -> str:
    for marker in ("«", "»", '"', "“", "”", "'", "‘", "’"):
        if marker in text:
            return marker
    return "none"


def _speaker_marker(text: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("-"):
        return "dash"
    if stripped.startswith("—"):
        return "emdash"
    return "none"
