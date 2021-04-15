import pytest

from utility.dragen_utility import custom_sort, get_ref, set_rgism


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
        "def_parameters": {"RefGenome": {"test_genome": {"ref-dir": "test.m_149"}}},
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
    ref == "test.m_149"


def test_set_rgism(excel_dict):
    assert set_rgism(excel_dict) == excel_dict["SampleID"]
