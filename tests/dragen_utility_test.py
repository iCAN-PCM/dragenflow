import pytest

from src.utility.dragen_utility import (
    fastq_file,
    file_parse,
    get_flow_cell,
    get_ref,
    load_json,
    run_type,
    set_rgism,
    SHA_RTYPE,
    trim_options,
)


@pytest.fixture
def template_dict():
    data = {
        "test_pipeline": {
            "enable-sort": "true",
            "enable-duplicate-marking": "true",
            "enable-duplicate-marking": "true",
            "enable-sv": "false",
            "sv-exome": "true",
            "enable-cnv": "false",
            "RGID": "{rgid}",
            "RGSM": "{rgsm}",
            "qc-coverage-region-1": "{TargetRegions}",
            "output-file-prefix": "{outprefix}",
            "fastq-file1": "{read1}",
            "fastq-file2": "{read2}",
            "ref-dir": "{refgenome}",
            # tumor alignment specifics
            "tumor-fastq1": "{read1}",
            "tumor-fastq2": "{read2}",
            "RGID-tumor": "{rgid}",
            "RGSM-tumor": "{rgsm}",
            # tumor variant call
            "tumor-bam-input": "{tumorbam}",
            # paired variant call
            "bam-input": "{normalbam}",
        },
        "adapters": {
            "truseq": "/fas/NGS/pipes/dragen/configs/adapters/truseq_adapters.fasta"
        },
        "ref_parameters": {"RefGenome": {"test_genome": {"ref-dir": "test.m_149"}}},
    }
    return data


@pytest.fixture
def excel_dict():
    data = {
        "TargetRegions": "some/path",
        "index": 2,
        "Index": "TTGATCCG",
        "RefGenome": "test_genome",
        "SampleID": "test_id",
        "Sample_Name": "testsample1.5",
        "dry_run": False,
        "row_index": 2,
        "Sample_Project": "test_project",
        "_run_type": "test",
    }
    return data


@pytest.fixture
def excel_dict2():
    data = {
        "Sample_ID": "test_id",
    }
    return data


def test_get_ref(excel_dict, template_dict):
    ref = get_ref(excel_dict, template_dict)
    assert ref == "test.m_149"


def test_set_rgism(excel_dict, excel_dict2):
    assert set_rgism(excel_dict) == excel_dict["SampleID"]
    assert set_rgism(excel_dict2) == excel_dict2["Sample_ID"]


def test_load_json():
    json_dict = load_json("./src/dragen_config.json")["profile1"]
    assert type(json_dict["ican-exome_normal_pipeline"]) == dict


def test_get_flow_cell():
    path = "./path/210317_A00464_0300_BHW7FTDMXX/one/two/test_samplesheet.csv"
    flow_cell = get_flow_cell(path)
    # assert flow_cell == "BHW7FTDMXX"
    assert flow_cell == "one"


def test_parse_file():
    path = "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv"
    data = file_parse(path)
    assert type(data) == list
    # total row = 12 and row containing dragen = 9
    assert len(data) == 9


def test_fastq_file(excel_dict):
    fastq_1 = fastq_file(excel_dict, 1, False)
    assert fastq_1 == "testsample1.5_S2_R1_001.fastq.gz"


def test_trim_options(excel_dict, template_dict):
    # trigger trim option
    excel_dict = excel_dict
    excel_dict["AdapterTrim"] = "truseq"
    adapter = trim_options(excel_dict, template_dict)

    assert adapter == template_dict["adapters"]["truseq"]


@pytest.mark.parametrize(
    "Is_tumor,expected,matching_normal_sample",
    [
        ("0", "germline", ""),
        ("No", "germline", ""),
        ("", "germline", ""),
        ("1", "somatic_single", ""),
        ("Yes", "somatic_single", ""),
        ("Yes", "somatic_paired", "test_id"),
    ],
)
def test_run_type(excel_dict, Is_tumor, expected, matching_normal_sample):
    excel_dict["Is_tumor"] = Is_tumor
    excel_dict["matching_normal_sample"] = matching_normal_sample
    returned_excel = run_type([excel_dict])
    print(returned_excel)
    assert returned_excel[0][SHA_RTYPE] == expected


@pytest.mark.parametrize(
    "Is_tumor,expected,matching_normal_sample",
    [
        ("Yes", RuntimeError, "test_id1"),
    ],
)
def test_run_type_error(excel_dict, Is_tumor, expected, matching_normal_sample):
    excel_dict["Is_tumor"] = Is_tumor
    excel_dict["matching_normal_sample"] = matching_normal_sample
    with pytest.raises(expected):
        run_type([excel_dict])
