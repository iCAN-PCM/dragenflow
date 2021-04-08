from flow import Flow
import logging

from utility.dragen_utility import (
    dragen_cli,
    load_json,
    normal_pipeline,
    tumor_alignment,
    tumor_variant,
    paired_variant,
)


logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
logging.info("started new logging session")


class ConstructDragen(Flow):
    def __init__(self):
        self.n = 1
        self.current_n = f"N{self.n}"
        self.current_t = f"T{self.n}"
        self.last_bam_file = ""
        self.profile = load_json()["profile1"]

    def constructor(self, excel: dict) -> [str]:
        # "N" (or empty), it triggers normal_pipeline_template
        print(excel.get("tumor/normal"))
        if excel.get("tumor/normal") == "N":
            logging.info(f"{excel.get('tumor/normal')}: executing normal_pipeline")
            cmd_d = normal_pipeline(self.profile, excel, "normal_pipeline")
            final_str = dragen_cli(cmd_d)

            return [final_str]

        #  if it's "T" 1) run tumor alignment 2) run tumor variant call
        if excel.get("tumor/normal") == "T":
            logging.info(
                f"{excel.get('tumor/normal')}:preparing tumor alignment template"
            )
            # Todo:
            # define prefix rgid, rgism => rgid is sample id, placeholder idx1_idx2
            arg_strings = []
            cmd_d1 = tumor_alignment(self.profile, excel, "tumor_alignment")

            default_str1 = " ".join(f"--{key} {val}" for (key, val) in cmd_d1.items())
            final_str1 = f"dragen {default_str1}"
            arg_strings.append(final_str1)
            # 2. prepare tumor_variant_call_template
            # define tumor bam input => outputfile-prefix.bam (from previous run)
            logging.info("preparing tumor variant call template")
            cmd_d2 = tumor_variant(self.profile, excel, cmd_d1, "tumor_variant_call")
            final_str2 = dragen_cli(cmd_d2)
            arg_strings.append(final_str2)
            return arg_strings

        # if it's N1 1) normal pipeline
        if excel.get("tumor/normal") == self.current_n:
            # Todo:
            # define prefix
            # define RGID, RGSM
            cmd_d = normal_pipeline(self.profile, excel, "normal_pipeline")
            logging.info(f"{self.current_n}: preparing normal_pipeline")
            final_str = dragen_cli(cmd_d)
            self.last_bam_file = f"{cmd_d['output-file-prefix']}.bam"
            return [final_str]

        # if it's T1  run tumor alignment & paired variant calls
        if excel.get("tumor/normal") == self.current_t:
            # Todo:
            # define prefix
            # define rgid rgsm
            arg_string = []
            # step 1 tumor alignment
            logging.info(f"{self.current_t}: preparing tumor alignment template")
            cmd_d1 = tumor_alignment(self.profile, excel, "tumor_alignment")

            final_str1 = dragen_cli(cmd_d1)
            arg_string.append(final_str1)

            # step 2 paired variant call
            logging.info(f"{self.current_t}: preparing paired varaint call template")
            cmd_d2 = paired_variant(self.profile, excel, self.last_bam_file, cmd_d1)

            final_str2 = dragen_cli(cmd_d2)
            arg_string.append(final_str2)

            self.n += 1
            self.current_n = f"N{self.n}"
            self.current_t = f"T{self.n}"
            logging.info(f"counter incremented to:{self.n}")
            logging.info(self.current_n)
            logging.info(self.current_t)
            return arg_string
