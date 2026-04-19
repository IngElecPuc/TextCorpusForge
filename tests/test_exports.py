import importlib.util

import pytest

from textforge.io.parquet_writer import write_parquet


pyarrow_available = importlib.util.find_spec("pyarrow") is not None


@pytest.mark.skipif(not pyarrow_available, reason="pyarrow no está disponible en este entorno")
def test_write_parquet(tmp_path):
    output = tmp_path / "rows.parquet"
    write_parquet([{"a": 1}, {"a": 2}], output)
    assert output.exists()



def test_write_parquet_normalizes_empty_metadata_dict(tmp_path):
    pytest.importorskip("pyarrow")
    import pandas as pd

    output = tmp_path / "rows_with_metadata.parquet"
    write_parquet([{"id": 1, "metadata": {}}, {"id": 2, "metadata": {"line_numbers": [1]}}], output)

    df = pd.read_parquet(output)
    assert len(df) == 2
    assert df.loc[0, "metadata"] is None or df.loc[0, "metadata"] == {}
