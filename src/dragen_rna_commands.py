from src.utility.dragen_utility import (
    fastq_file,
    get_ref,
    set_fileprefix,
    set_rgid,
    set_rgism,
)
from .utility.commands import Commands


class BaseDragenRnaCommand(Commands):
    """
    Bade Dragen rna comands
    """

    def __init__(self, excel: dict, template: dict) -> None:
        self.excel = excel
        self.template = template
        self.arg_registry = {
            "ref-dir": get_ref(self.excel, self.template),
            "intermediate-results-dir": "/staging/intermeidate",
            "output-file-prefix": set_fileprefix(self.excel),
            "fastq-file1": fastq_file(self.excel, 1),
            "fastq-file2": fastq_file(self.excel, 2),
            "RGID": set_rgid(self.excel),
            "RGISM": set_rgism(self.excel),
        }

    def construct_commands(self) -> dict:
        # get the arg from json config filie
        cmd_dict = self.template
        # get the dict that needs to be filled in at runtime
        param_list = [i for i in cmd_dict if str(cmd_dict[i]).startswith("{")]
        if len(param_list) == 0:
            raise RuntimeError("Someting went wrong with parsing template")
        for val in param_list:
            try:
                cmd_dict[val] = self.arg_registry.get(val)
            except KeyError:
                print(f"miising key {val}: in registry")
                continue
        return cmd_dict


class ExtraRnaCommands(Commands):
    """
    Custom Rna command specific certain instane
    """

    def construct_commands(self) -> dict:
        extra_cmd_dict = {}
        return extra_cmd_dict
