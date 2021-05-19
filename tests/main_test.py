import pytest

from main import HandleFlow


@pytest.fixture(scope="function")
def get_handle():
    return HandleFlow()


def test_parse_file(get_handle):
    list_dict = get_handle.parse_file(
        "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv", "dragen"
    )
    assert type(list_dict) == list
    assert len(list_dict) == 9
    print(len(list_dict))
    assert "file_path" in list_dict[0].keys()


def test_execute_bash(get_handle):
    get_handle1 = get_handle
    list_str = get_handle1.execute_bash(
        "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv", "dragen"
    )

    assert sum([len(elem) for elem in list_str]) == 13

    for val in list_str:
        if type(val[0]) == int:
            assert val[0] == 0
        else:
            assert val[0][0] == 0


def test_construct_str(get_handle):
    list_str = get_handle.execute_bash(
        "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv",
        "dragen",
        dry_run=True,
    )
    for val in list_str:
        assert type(val) == str
        assert "{" not in val
