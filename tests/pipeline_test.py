import pytest

from utility.pipeline import (
    BasePipeline,
    CompositePipeline,
    PairedVariantPipeline,
    TumorVariantPipeline,
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
            # "bam-input": "{normalbam}",
            "name": "test_pipeline",
        },
        "test_pipeline2": {"tumor-bam-input": "{tumorbam}", "name": "test_pipeline2"},
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
        "SampleID": "test_sampleID",
    }
    return data


def test_base_pipeline(excel_dict, template_dict):
    excel_dict = excel_dict
    dragen = template_dict
    # excel_dict["tumor/normal"] = "N"
    dragen_cmd = BasePipeline(excel_dict, template_dict, "test_pipeline")
    dragen = dragen_cmd.construct_pipeline()
    assert dragen["qc-coverage-region-1"] == "some/path"
    assert dragen["tumor-fastq2"] == "test_S2_R2_001.fastq"
    assert dragen["ref-dir"] == "test.m_149"


def test_composite_pipeline(excel_dict, template_dict):
    final_cmd = CompositePipeline()
    base_cmd = BasePipeline(excel_dict, template_dict, "test_pipeline")
    final_cmd.add(base_cmd)
    final_dict = final_cmd.construct_pipeline()
    assert final_dict["qc-coverage-region-1"] == "some/path"
    assert final_dict["tumor-fastq2"] == "test_S2_R2_001.fastq"
    assert final_dict["ref-dir"] == "test.m_149"


def test_composite_pipeline_tv(excel_dict, template_dict):
    final_cmd = CompositePipeline()
    base_cmd = BasePipeline(excel_dict, template_dict, "test_pipeline")
    tumor_output = "test_tumor1"
    tv_cmd = TumorVariantPipeline(tumor={"output-file-prefix": tumor_output})
    final_cmd.add(base_cmd)
    final_cmd.add(tv_cmd)
    final_dict = final_cmd.construct_pipeline()
    assert final_dict["qc-coverage-region-1"] == "some/path"
    assert final_dict["tumor-fastq2"] == "test_S2_R2_001.fastq"
    assert final_dict["ref-dir"] == "test.m_149"
    assert final_dict["tumor-bam-input"] == f"{tumor_output}.bam"
    # print(final_dict)
    # print(type(final_dict))
    assert type(final_dict) == dict


def test_composite_pipeline_pv(excel_dict, template_dict):
    final_cmd = CompositePipeline()
    base_cmd = BasePipeline(excel_dict, template_dict, "test_pipeline")
    last_bam = "test_last_bam.bam"
    tumor_output = "test_tumor2"
    pv_cmd = PairedVariantPipeline(
        normal_bam=last_bam, tumor={"output-file-prefix": tumor_output}
    )
    final_cmd.add(base_cmd)
    final_cmd.add(pv_cmd)
    final_dict = final_cmd.construct_pipeline()
    assert final_dict["qc-coverage-region-1"] == "some/path"
    assert final_dict["tumor-fastq2"] == "test_S2_R2_001.fastq"
    assert final_dict["ref-dir"] == "test.m_149"
    assert final_dict["tumor-bam-input"] == f"{tumor_output}.bam"
    assert final_dict["bam-input"] == f"{last_bam}"
