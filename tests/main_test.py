import pytest

from main import HandleFlow


@pytest.fixture(scope="function")
def get_handle():
    return HandleFlow()


def test_parse_file(get_handle):
    list_dict = get_handle.parse_file(
        "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv", "dragen"
    )
    assert type(list_dict) == list
    # check for number of rows in the excel file its 12 row
    assert len(list_dict) == 12
    assert "file_path" in list_dict[0].keys()
    # index of first germline in test samplesheet
    assert list_dict[1]["row_index"] == 3


def test_execute_bash(get_handle):
    list_str = get_handle.execute_bash(
        "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv",
        "dragen",
        dry_run=False,
    )
    print(f"len of : {len(list_str)}")
    assert len(list_str) == 17
    for val in list_str:
        if type(val[0]) == int:
            assert val[0] == 0
        else:
            assert val[0][0] == 0


def test_construct_str(get_handle):
    list_str = get_handle.execute_bash(
        "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv",
        "dragen",
        dry_run=True,
    )
    with open("test1.txt", "w") as f:
        for val in list_str:
            f.write(f"{val} \n")
    assert len(list_str) == 17
    for val in list_str:
        assert type(val) == str
        assert "{" not in val


def test_execute_bash_2(get_handle):
    with pytest.raises(FileNotFoundError):
        get_handle.execute_bash(
            "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv",
            "dragen",
            dry_run=False,
            bash_cmd="queue",
        )
