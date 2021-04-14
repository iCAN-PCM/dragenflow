import pytest

from utility.pipeline import BasePipeline, TumorVariantPipeline, CompositePipeline


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
    print(dragen)
    # assert dragen.n == 1
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


def test_composite_pipeline2(excel_dict, template_dict):
    final_cmd = CompositePipeline()
    base_cmd = BasePipeline(excel_dict, template_dict, "test_pipeline")
    test2_cmd = TumorVariantPipeline(tumor={"output-file-prefix": "test_tumor"})
    final_cmd.add(base_cmd)
    final_cmd.add(test2_cmd)
    print("length" + str(len(final_cmd._children)))
    final_dict = final_cmd.construct_pipeline()
    print(final_dict)
    assert 1 == 2
