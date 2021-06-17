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
    script_path,
    trim_options,
)
from .utility.flow import Flow


class ConstructDragenPipeline(Flow):
    def __init__(self):
        self.all_bam_file = {}
        self.profile = None

    def check_trimming(self, excel: dict, read_trimmer) -> dict:
        trim = trim_options(excel, self.profile)
        cmd = {}
        cmd["read-trimmers"] = read_trimmer
        if trim:
            cmd["read-trimmers"] = cmd["read-trimmers"] + ",adapter"
            cmd["trim-adapter-read1"] = trim
            cmd["trim-adapter-read2"] = trim
        return cmd

    def command_with_trim(self, excel: dict, pipe_elem: str) -> dict:
        pipeline = excel.get("pipeline_parameters")
        base_cmd = BaseDragenCommand(excel, self.profile, f"{pipeline}_{pipe_elem}")
        cmd = base_cmd.construct_commands()
        trim_cmd = self.check_trimming(excel, cmd.get("read-trimmers"))

        return {**cmd, **trim_cmd}

    def constructor(self, excel: dict) -> List[str]:
        self.profile = load_json(script_path("dragen_config.json"))["profile1"]
        # "N" (or empty), it triggers normal_pipeline_template
        pipeline = excel.get("pipeline_parameters")
        if excel["run_type"] == "germline":
            # out put prefix = samplename
            # out put prefix paired = sample.s
            logging.info(f"{excel.get('run_type')}: executing normal_pipeline")
            cmd_d = self.command_with_trim(excel, "normal_pipeline")
            # store bam file
            self.all_bam_file[excel["SampleID"]] = f"{cmd_d['output-file-prefix']}.bam"
            final_str = dragen_cli(cmd_d, excel)
            return [final_str]

        #  if it's "T" => step 1 run tumor alignment
        #                 step 2 run tumor variant call
        elif excel["run_type"] == "somatic_single":
            logging.info(f"{excel.get('run_type')}:preparing tumor alignment template")
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

        # if it's T1 => step 1  run tumor alignment
        #               step 2 paired variant calls
        elif excel["run_type"] == "somatic_paired":
            logging.info(
                f"{excel.get('run_type')}:: preparing tumor alignment template"
            )
            # step 1 tumor alignment
            arg_string = []
            cmd_d1 = self.command_with_trim(excel, "tumor_alignment")
            final_str1 = dragen_cli(cmd_d1, excel, "alignment")
            arg_string.append(final_str1)

            # step 2 paired variant call
            logging.info(
                f"{excel.get('run_type')}:: preparing paired varaint call template"
            )
            cmd_d2 = CompositeCommands()
            base_cmd = BaseDragenCommand(
                excel, self.profile, f"{pipeline}_paired_variant_call"
            )
            pv_cmd = PairedVariantCommands(
                self.all_bam_file[excel["matching_normal_sample"]], cmd_d1
            )
            cmd_d2.add(base_cmd)
            cmd_d2.add(pv_cmd)
            final_str2 = dragen_cli(cmd_d2.construct_commands(), excel, "analysis")
            arg_string.append(final_str2)
            return arg_string
        else:
            logging.info(
                f"{excel.get('run_type')}, You shouldn't be here No pipeline info: \
                executing by default normal_pipeline"
            )
            final_str = dragen_cli(
                self.command_with_trim(excel, "normal_pipeline"), excel
            )
            return [final_str]
