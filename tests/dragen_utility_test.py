import pytest

from utility.dragen_utility import (
    custom_sort,
    get_ref,
    infer_pipeline,
    set_rgism,
    load_json,
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
        "RefGenome": "test_genome",
        "SampleID": "test_id",
    }
    return data


@pytest.mark.parametrize("test_input,expected", [("", 0), ("N1", 1), ("T4", 4)])
def test_custom_sort(test_input, expected):
    assert custom_sort(test_input) == expected
    assert type(custom_sort(test_input)) == int


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
