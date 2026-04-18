from __future__ import annotations

from textforge.orchestration.stages import stage0_canonicalize


PIPELINE_REGISTRY = {
    "canonicalize": stage0_canonicalize,
}
