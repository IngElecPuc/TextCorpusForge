from pathlib import Path

import yaml


ROOT = "/home/felpipe/Datasets/Textos paralelos"

EXPECTED = {
    "dgt.yaml": ("ces_alignment_xml", f"{ROOT}/DGT-2019.en-es"),
    "eubookshop.yaml": ("ids_sidecar", f"{ROOT}/EUbookshop.en-es"),
    "europarl.yaml": ("ces_alignment_xml", f"{ROOT}/Europarl.v8.en-es"),
    "multiun.yaml": ("parallel_sidecar_plain", f"{ROOT}/MultiUN.en-es"),
    "opensubtitles.yaml": ("parallel_sidecar_plain", f"{ROOT}/OpenSubtitles.en-es"),
    "unpc.yaml": ("ces_alignment_xml", f"{ROOT}/UNPC.en-es"),
}


def test_dataset_configs_match_confirmed_layout() -> None:
    cfg_dir = Path("configs/datasets")
    for filename, (reader, input_root) in EXPECTED.items():
        data = yaml.safe_load((cfg_dir / filename).read_text(encoding="utf-8"))
        assert data["dataset"]["reader"] == reader
        assert data["dataset"]["input_roots"] == [input_root]
