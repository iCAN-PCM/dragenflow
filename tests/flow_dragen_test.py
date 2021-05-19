import pytest

from src.dragen_pipeline import ConstructDragenPipeline


@pytest.fixture
def excel_dict():
    data = {
        "TargetRegions": "some/path",
        "Index": "TTGATCCG",
        "RefGenome": "GRCh38",
        "SampleID": "test_sampleID",
        "Sample_Name": "testsample1.5",
        "pipeline_parameters": "genome",
        "file_path": "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv",
        "Sample_Project": "testproject",
        "fastq_dir": "./path/210317_A00464_0300_BHW7FTDMXX/testsample",
        "Lane": 1,
    }
    return data


@pytest.fixture
def dragen_flow():
    dragen = ConstructDragenPipeline()
    return dragen


def test_dragen_normal(dragen_flow, excel_dict):
    excel_dict = excel_dict
    dragen = dragen_flow
    excel_dict["tumor/normal"] = "N"
    dragen_cmd = dragen.constructor(excel_dict)
    assert type(dragen_cmd) == list
    assert dragen.n == 1
    assert dragen.current_n == "N1"
    assert "{" not in str(dragen_cmd[0])
    assert dragen.last_bam_file == ""


def test_dragen_tumor(dragen_flow, excel_dict):
    excel_dict = excel_dict
    dragen = dragen_flow
    excel_dict["tumor/normal"] = "T"
    dragen_cmd = dragen.constructor(excel_dict)
    assert type(dragen_cmd) == list
    assert len(dragen_cmd) == 2
    assert dragen.n == 1
    assert dragen.current_n == "N1"
    assert "{" not in str(dragen_cmd[0])
    assert dragen.last_bam_file == ""


def test_dragen_normal_tumor1(dragen_flow, excel_dict):
    excel_dict = excel_dict
    dragen = dragen_flow
    excel_dict["tumor/normal"] = "N1"
    dragen_cmd = dragen.constructor(excel_dict)
    assert type(dragen_cmd) == list
    assert len(dragen_cmd) == 1
    assert dragen.n == 1
    assert dragen.current_n == "N1"
    assert "{" not in str(dragen_cmd[0])
    # assert dragen.last_bam_file == "output-prefix_2.bam"


def test_dragen_normal_tumor2(dragen_flow, excel_dict):
    excel_dict = excel_dict
    dragen = dragen_flow
    excel_dict["tumor/normal"] = "T1"
    assert dragen_flow.n == 1
    assert dragen_flow.current_t == "T1"
    dragen_cmd = dragen.constructor(excel_dict)
    assert type(dragen_cmd) == list
    assert len(dragen_cmd) == 2
    assert dragen.n == 2
    assert dragen.current_t == "T2"
    assert dragen.last_bam_file == ""
    assert type(dragen_cmd[0]) == str
    assert type(dragen_cmd[1]) == str
    assert "{" not in str(dragen_cmd[0])
    assert "{" not in str(dragen_cmd[1])
