import logging
from typing import List, Optional

from .dragen_rna_commands import BaseDragenRnaCommand
from .utility.dragen_utility import dragen_cli, load_json, script_path
from .utility.flow import Flow


class ConstructRnaPipeline(Flow):
    def constructor(self, excel: dict) -> Optional[List[str]]:
        self.profile = load_json(script_path("dragen_rna.json"))["rna"]
        logging.info("executing dragen rna command")
        cmd_base = BaseDragenRnaCommand(excel, self.profile)
        cmd = cmd_base.construct_commands()
        final_str = dragen_cli(cmd=cmd, excel=excel)
        return [final_str]
