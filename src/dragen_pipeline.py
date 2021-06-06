import logging
import re
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
    script_path,
    trim_options,
)
from .utility.flow import Flow


class ConstructDragenPipeline(Flow):
    def __init__(self):
        self._n = 0
        self.last_bam_file = ""
        self.profile = load_json(script_path("dragen_config.json"))["profile1"]
        self.current_seq = ""
        self._n_pattern = re.compile("^N[0-9]+$")
        self._t_pattern = re.compile("^T[0-9]+$")

    def check_trimming(self, excel: dict, cmd: dict) -> None:
        trim = trim_options(excel, self.profile)
        if trim:
            cmd["read-trimmers"] = cmd["read-trimmers"] + ",adapter"
            cmd["trim-adapter-read1"] = trim
            cmd["trim-adapter-read2"] = trim
        return

    def reset(self):
        self.last_bam_file = ""

    def command_with_trim(self, excel: dict, pipe_elem: str) -> dict:
        pipeline = excel.get("pipeline_parameters")
        cmd_d = BaseDragenCommand(excel, self.profile, f"{pipeline}_{pipe_elem}")
        cmd_d = cmd_d.construct_commands()
        self.check_trimming(excel, cmd_d)
        return cmd_d

    def constructor(self, excel: dict) -> List[str]:
        # "N" (or empty), it triggers normal_pipeline_template
        pipeline = excel.get("pipeline_parameters")
        if excel.get("tumor/normal") == "N":
            # out put prefix = samplename
            # out put prefix paired = sample.s
            logging.info(f"{excel.get('tumor/normal')}: executing normal_pipeline")
            cmd_d = self.command_with_trim(excel, "normal_pipeline")
            final_str = dragen_cli(cmd_d, excel)
            return [final_str]

        #  if it's "T" => step 1 run tumor alignment
        #                 step 2 run tumor variant call
        elif excel.get("tumor/normal") == "T":
            logging.info(
                f"{excel.get('tumor/normal')}:preparing tumor alignment template"
            )
            arg_strings = []
            # step 1
            cmd_d1 = self.command_with_trim(excel, "tumor_alignment")
            final_str1 = dragen_cli(cmd_d1, excel, "alignment")
            arg_strings.append(final_str1)
            # step 2: prepare tumor_variant_call_template
            # define tumor bam input => outputfile-prefix.bam (from previous run)
            logging.info("preparing tumor variant call template")
            cmd_d2 = CompositeCommands()
            base_cmd = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_tumor_variant_call"
            )
            tv_cmd = TumorVariantCommands(tumor=cmd_d1)
            cmd_d2.add(base_cmd)
            cmd_d2.add(tv_cmd)
            final_str2 = dragen_cli(cmd_d2.construct_commands(), excel, "analysis")
            arg_strings.append(final_str2)
            return arg_strings

        # if it's N1 => step 1 normal pipeline
        elif self._n_pattern.match(excel.get("tumor/normal")):
            logging.info(f"{excel.get('tumor/normal')}: preparing normal_pipeline")
            cmd_d = self.command_with_trim(excel, "normal_pipeline")
            final_str = dragen_cli(cmd_d, excel)
            self.last_bam_file = f"{cmd_d['output-file-prefix']}.bam"
            self._n = int(excel["tumor/normal"][1:])
            logging.info(f"setting new n value: {self._n}")
            return [final_str]

        # if it's T1 => step 1  run tumor alignment
        #               step 2 paired variant calls
        elif self._t_pattern.match(excel.get("tumor/normal")):
            logging.info(
                f"{excel.get('tumor/normal')}:: preparing tumor alignment template"
            )
            # quick check if proper order exist
            if int(excel["tumor/normal"][1:]) != self._n:
                raise RuntimeError("incorrect row ordering")
            # step 1 tumor alignment
            arg_string = []
            cmd_d1 = self.command_with_trim(excel, "tumor_alignment")
            final_str1 = dragen_cli(cmd_d1, excel, "alignment")
            arg_string.append(final_str1)

            # step 2 paired variant call
            logging.info(
                f"{excel.get('tumor/normal')}:: preparing paired varaint call template"
            )
            cmd_d2 = CompositeCommands()
            base_cmd = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_paired_variant_call"
            )
            pv_cmd = PairedVariantCommands(self.last_bam_file, cmd_d1)
            cmd_d2.add(base_cmd)
            cmd_d2.add(pv_cmd)
            final_str2 = dragen_cli(cmd_d2.construct_commands(), excel, "analysis")
            arg_string.append(final_str2)
            return arg_string
        else:
            logging.info(
                f"{excel.get('tumor/normal')}, No pipeline info: \
                executing by default normal_pipeline"
            )
            final_str = dragen_cli(
                self.command_with_trim(excel, "normal_pipeline"), excel
            )
            return [final_str]
