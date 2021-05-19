import logging
from typing import List

from .dragen_commands import (
    BaseDragenCommand,
    PairedVariantCommands,
    TumorVariantCommands,
)
from .utility.commands import CompositeCommands
from .utility.dragen_utility import (
    dragen_cli,
    load_json,
)
from .utility.flow import Flow


class ConstructDragenPipeline(Flow):
    def __init__(self):
        self.n = 1
        self.current_n = f"N{self.n}"
        self.current_t = f"T{self.n}"
        self.last_bam_file = ""
        self.profile = load_json("config.json")["profile1"]
        self.current_seq = ""

    def constructor(self, excel: dict) -> List[str]:
        # "N" (or empty), it triggers normal_pipeline_template
        pipeline = excel.get("pipeline_parameters")
        if excel.get("tumor/normal") == "N":
            # out put prefix = samplename
            # out put prefix =paired = sample.s
            # target retion empty = genome
            # umi profile
            logging.info(f"{excel.get('tumor/normal')}: executing normal_pipeline")
            # cmd_d = normal_pipeline(self.profile, excel, "normal_pipeline")
            cmd_d = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_normal_pipeline"
            )
            cmd_d = cmd_d.construct_commands()
            final_str = dragen_cli(cmd_d, excel)

            return [final_str]

        #  if it's "T" 1) run tumor alignment 2) run tumor variant call
        elif excel.get("tumor/normal") == "T":
            logging.info(
                f"{excel.get('tumor/normal')}:preparing tumor alignment template"
            )
            # Todo:
            arg_strings = []
            # cmd_d1 = tumor_alignment(self.profile, excel, "tumor_alignment")
            cmd_d1 = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_tumor_alignment"
            )
            cmd_d1 = cmd_d1.construct_commands()
            final_str1 = dragen_cli(cmd_d1, excel)
            arg_strings.append(final_str1)
            # 2. prepare tumor_variant_call_template
            # define tumor bam input => outputfile-prefix.bam (from previous run)
            logging.info("preparing tumor variant call template")
            # cmd_d2 = tumor_variant(self.profile, excel, cmd_d1, "tumor_variant_call")
            cmd_d2 = CompositeCommands()
            base_cmd = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_tumor_variant_call"
            )
            tv_cmd = TumorVariantCommands(tumor=cmd_d1)
            cmd_d2.add(base_cmd)
            cmd_d2.add(tv_cmd)
            final_str2 = dragen_cli(cmd_d2.construct_commands(), excel)
            arg_strings.append(final_str2)
            return arg_strings

        # if it's N1 1) normal pipeline
        elif excel.get("tumor/normal") == self.current_n:
            cmd_d = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_normal_pipeline"
            )
            cmd_d = cmd_d.construct_commands()
            logging.info(f"{self.current_n}: preparing normal_pipeline")
            final_str = dragen_cli(cmd_d, excel)
            self.last_bam_file = f"{cmd_d['output-file-prefix']}.bam"
            return [final_str]

        # if it's T1  run tumor alignment & paired variant calls
        elif excel.get("tumor/normal") == self.current_t:
            # Todo:
            arg_string = []
            # step 1 tumor alignment
            logging.info(f"{self.current_t}: preparing tumor alignment template")
            # cmd_d1 = tumor_alignment(self.profile, excel, "tumor_alignment")
            cmd_d1 = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_tumor_alignment"
            )
            cmd_d1 = cmd_d1.construct_commands()
            final_str1 = dragen_cli(cmd_d1, excel)
            arg_string.append(final_str1)

            # step 2 paired variant call
            logging.info(f"{self.current_t}: preparing paired varaint call template")
            # cmd_d2 = paired_variant(self.profile, excel, self.last_bam_file, cmd_d1)
            cmd_d2 = CompositeCommands()
            base_cmd = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_paired_variant_call"
            )
            pv_cmd = PairedVariantCommands(self.last_bam_file, cmd_d1)
            cmd_d2.add(base_cmd)
            cmd_d2.add(pv_cmd)
            final_str2 = dragen_cli(cmd_d2.construct_commands(), excel)
            arg_string.append(final_str2)
            self.n += 1
            self.current_n = f"N{self.n}"
            self.current_t = f"T{self.n}"
            logging.info(f"counter incremented to:{self.n}")
            logging.info(self.current_n)
            logging.info(self.current_t)
            return arg_string
        else:
            logging.info(
                f"{excel.get('tumor/normal')},{self.n}, No pipeline info: \
                executing by default normal_pipeline"
            )
            cmd_d = BaseDragenCommand(
                excel,
                self.profile,
                f"{pipeline}_normal_pipeline",
            )
            cmd_d = cmd_d.construct_commands()
            final_str = dragen_cli(cmd_d, excel)
            return [final_str]
