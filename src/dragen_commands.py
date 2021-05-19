from .utility.commands import Commands
from .utility.dragen_utility import (
    fastq_file,
    get_ref,
    set_fileprefix,
    set_rgid,
    set_rgism,
)


class BaseDragenCommand(Commands):
    def __init__(self, excel: dict, template: dict, seq_pipeline: str) -> None:
        self.excek = excel
        self.template = template
        self.seq_pipeline = seq_pipeline
        self.arg_registry = {
            "fastq-file1": fastq_file(self.excek, 1),
            "fastq-file2": fastq_file(self.excek, 2),
            "tumor-fastq1": fastq_file(self.excek, 1),
            "tumor-fastq2": fastq_file(self.excek, 2),
            "output-file-prefix": set_fileprefix(self.excek),
            "qc-coverage-region-1": self.excek["TargetRegions"],
            "ref-dir": get_ref(self.excek, self.template),
            "RGID": set_rgid(self.excek),
            "RGSM": set_rgism(self.excek),
            "RGID-tumor": set_rgid(self.excek),
            "RGSM-tumor": set_rgism(self.excek),
        }

    def construct_commands(self) -> dict:
        # select the parameter from config template
        cmd_dict = self.template[self.seq_pipeline]
        # get the dict that needs to be fixed
        param_list = [i for i in cmd_dict if str(cmd_dict[i]).startswith("{")]
        for val in param_list:
            try:
                cmd_dict[val] = self.arg_registry.get(val)
            except KeyError:
                print(f"missing key {val}: in registry")
                continue
        return cmd_dict


class TumorVariantCommands(Commands):
    def __init__(self, tumor: dict) -> None:
        self.tumor = tumor

    def construct_commands(self) -> dict:

        cmd_dict = {"tumor-bam-input": f"{self.tumor['output-file-prefix']}.bam"}

        return cmd_dict


class PairedVariantCommands(Commands):
    def __init__(self, normal_bam: str, tumor: dict) -> None:
        self.tumor = tumor
        self.normal_bam = normal_bam

    def construct_commands(self) -> dict:
        cmd_dict = {}
        cmd_dict["bam-input"] = self.normal_bam
        cmd_dict["tumor-bam-input"] = f"{self.tumor['output-file-prefix']}.bam"
        return cmd_dict
