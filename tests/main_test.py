import pandas as pd
import pytest

from main import HandleFlow


@pytest.fixture
def get_handle():
    return HandleFlow()


def test_parse_file(get_handle):
    pd_df = get_handle.parse_file(
        "./path/210317_A00464_0300_BHW7FTDMXX/one/two/test_samplesheet.csv", "dragen"
    )
    assert type(pd_df) == pd.DataFrame
    assert "file_path" in pd_df.columns


def test_construct_str(get_handle):
    list_str = get_handle.construct_str(
        "./path/210317_A00464_0300_BHW7FTDMXX/one/two/test_samplesheet.csv", "dragen"
    )
    for val in list_str:
        assert type(val) == str
        assert "{" not in val
