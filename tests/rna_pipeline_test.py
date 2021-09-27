import pytest

from src.dragen_rna_commands import BaseDragenRnaCommand


@pytest.fixture
def template_dict():
    data = {
        "rna": {
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
            "ref_parameters": {
                "RefGenome": {"test_genome": {"ref-dir": "test.m_149"}},
                "noiseprofile": "'put noise profile for variant calling here'",
            },
        }
    }
    return data


@pytest.fixture
def excel_dict():
    data = {
        "TargetRegions": "some/path",
        "Index": "TTGATCCG",
        "Sample_Name": "testsample1.5",
        "RefGenome": "test_genome",
        "SampleID": "test_sampleID",
        "file_path": "./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet.csv",
        "Sample_Project": "testproject",
        "fastq_dir": "./path/210317_A00464_0300_BHW7FTDMXX/testsample",
        "Lane": 1,
        "dry_run": False,
        "row_index": 2,
    }
    return data


def test_rna_base_commands(excel_dict, template_dict):
    template = template_dict["rna"]
    dragen_rna_cmd = BaseDragenRnaCommand(excel_dict, template)
    cmd = dragen_rna_cmd.construct_commands()
    print(cmd)
    assert cmd["enable-sort"] == template["enable-sort"]
