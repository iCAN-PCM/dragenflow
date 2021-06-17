import copy

from .utility.commands import Commands
from .utility.dragen_utility import (
    fastq_file,
    get_ref,
    set_fileprefix,
    set_rgid,
    set_rgism,
)


class BaseDragenCommand(Commands):
    """
    Base Dragen commands
    """

    def __init__(self, excel: dict, template: dict, seq_pipeline: str) -> None:
        self.excel = excel
        self.template = template
        self.seq_pipeline = seq_pipeline
        self.arg_registry = {
            "fastq-file1": fastq_file(self.excel, 1),
            "fastq-file2": fastq_file(self.excel, 2),
            "tumor-fastq1": fastq_file(self.excel, 1),
            "tumor-fastq2": fastq_file(self.excel, 2),
            "output-file-prefix": set_fileprefix(self.excel),
            "qc-coverage-region-1": self.excel["TargetRegions"],
            "ref-dir": get_ref(self.excel, self.template),
            "RGID": set_rgid(self.excel),
            "RGSM": set_rgism(self.excel),
            "RGID-tumor": set_rgid(self.excel),
            "RGSM-tumor": set_rgism(self.excel),
            # depending on the use case this can be directly added to json-template file
            "intermediate-results-dir": "/staging/intermediate",
            "vc-systematic-noise": template["ref_parameters"]["noiseprofile"],
        }

    def construct_commands(self) -> dict:
        # select the parameter from config template
        cmd_dict1 = self.template[self.seq_pipeline]
        cmd_dict2 = copy.deepcopy(cmd_dict1)
        # get the dict that needs to be filled in at runtime
        param_list = [i for i in cmd_dict2 if str(cmd_dict2[i]).startswith("{")]
        if len(param_list) == 0:
            raise RuntimeError("Something wrong with parsing template")
        for val in param_list:
            try:
                cmd_dict2[val] = self.arg_registry.get(val)
            except KeyError:
                print(f"missing key {val}: in registry")
                continue
        return cmd_dict2


class TumorVariantCommands(Commands):
    """
    TumorVariant specific dragen command
    """

    def __init__(self, tumor: dict) -> None:
        self.tumor = tumor

    def construct_commands(self) -> dict:

        cmd_dict = {"tumor-bam-input": f"{self.tumor['output-file-prefix']}_tumor.bam"}

        return cmd_dict


class PairedVariantCommands(Commands):
    """
    PairedVariant specific dragen command
    """

    def __init__(self, normal_bam: str, tumor: dict) -> None:
        self.tumor = tumor
        self.normal_bam = normal_bam

    def construct_commands(self) -> dict:
        cmd_dict = {}
        cmd_dict["bam-input"] = self.normal_bam
        cmd_dict["tumor-bam-input"] = f"{self.tumor['output-file-prefix']}_tumor.bam"
        cmd_dict["output-file-prefix"] = f"{self.tumor['output-file-prefix']}.tn"
        return cmd_dict
