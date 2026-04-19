import importlib.util

import pytest

from textforge.io.parquet_writer import write_parquet


pyarrow_available = importlib.util.find_spec("pyarrow") is not None


@pytest.mark.skipif(not pyarrow_available, reason="pyarrow no está disponible en este entorno")
def test_write_parquet(tmp_path):
    output = tmp_path / "rows.parquet"
    write_parquet([{"a": 1}, {"a": 2}], output)
    assert output.exists()
