import pytest

from src.utility.dragen_utility import (
    custom_sort,
    fastq_file,
    file_parse,
    get_flow_cell,
    get_ref,
    infer_pipeline,
    load_json,
    set_rgism,
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
    }
    return data


@pytest.mark.parametrize("test_input,expected", [("", 0), ("N1", 0.5), ("T4", 4)])
def test_custom_sort(test_input, expected):
    assert custom_sort(test_input) == expected
    assert type(custom_sort(test_input)) == float


def test_get_ref(excel_dict, template_dict):
    ref = get_ref(excel_dict, template_dict)
    assert ref == "test.m_149"


def test_set_rgism(excel_dict):
    assert set_rgism(excel_dict) == excel_dict["SampleID"]


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("genome_normal_pipeline", "genome"),
        ("exome_paired_variant_call", "exome"),
        ("exome-umi_normal_pipeline", "exome-umi"),
        ("ican-exome_paired_variant_call", "ican-exome"),
        ("ican-exome_umi_tumor_variant_call", "ican-exome"),
    ],
)
def test_infer_pipeline(test_input, expected):
    assert infer_pipeline(test_input) == expected


def test_load_json():
    json_dict = load_json("config.json")["profile1"]
    assert type(json_dict["ican-exome_normal_pipeline"]) == dict


def test_get_flow_cell():
    path = "./path/210317_A00464_0300_BHW7FTDMXX/one/two/test_samplesheet.csv"
    flow_cell = get_flow_cell(path)
    assert flow_cell == "BHW7FTDMXX"


def test_parse_file():
    path = "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv"
    data = file_parse(path)
    assert type(data) == list
    print(data)
    assert data[8]["tumor/normal"] == "T3"
    assert data[0]["tumor/normal"] == "T"


def test_fastq_file(excel_dict):
    fastq_1 = fastq_file(excel_dict, 1, False)
    assert fastq_1 == "testsample1.5_STTGATCCG_R1_001.fastq.gz"
