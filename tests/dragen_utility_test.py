import pytest

from utility.dragen_utility import (
    normal_pipeline,
    paired_variant,
    tumor_alignment,
    tumor_variant,
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
            "qc-coverage-region-1": "{TargetRegions}",
            "output-file-prefix": "{outprefix}",
            "fastq-file1": "{read1}",
            "fastq-file2": "{read2}",
            "ref-dir": "{refgenome}",
            # tumor alignment specifics
            "tumor-fastq1": "{read1}",
            "tumor-fastq2": "{read2}",
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
        "Sample_Name": "test",
        "RefGenome": "test_genome",
    }
    return data


def test_normal_pipeline(template_dict, excel_dict):
    npl = normal_pipeline(template_dict, excel_dict, "test_pipeline")
    print(npl)
    assert type(npl) == dict
    assert npl.get("ref-dir") == "test.m_149"
    assert npl.get("qc-coverage-region-1") == "some/path"
    assert npl.get("fastq-file1") == "test_S2_R1_001.fastq"
    assert npl.get("fastq-file2") == "test_S2_R2_001.fastq"


def test_tumor_alignment(template_dict, excel_dict):
    tumor_al = tumor_alignment(template_dict, excel_dict, "test_pipeline")
    print(tumor_al)
    assert tumor_al.get("ref-dir") == "test.m_149"
    assert tumor_al.get("qc-coverage-region-1") == "some/path"
    assert tumor_al.get("tumor-fastq1") == "test_S2_R1_001.fastq"
    assert tumor_al.get("tumor-fastq2") == "test_S2_R2_001.fastq"


def test_tumor_variant(template_dict, excel_dict):
    tumor = {"output-file-prefix": "t-prefix"}
    tumor_va = tumor_variant(template_dict, excel_dict, tumor, "test_pipeline")
    print(tumor_va)
    assert tumor_va.get("tumor-bam-input") == "t-prefix.bam"
    assert tumor_va.get("ref-dir") == "test.m_149"
    # assert tumor_va.get("output-file-prefix") == "output-prefix_2"


def test_paired_variant(template_dict, excel_dict):
    tumor = {"output-file-prefix": "t-prefix"}
    tumor_pa = paired_variant(
        template_dict, excel_dict, "norm.bam", tumor, "test_pipeline"
    )
    assert tumor_pa.get("bam-input") == "norm.bam"
    assert tumor_pa.get("tumor-bam-input") == "t-prefix.bam"
    assert tumor_pa.get("ref-dir") == "test.m_149"
