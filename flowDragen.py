from flow import Flow
import json
import logging
from string import Formatter

import logging
import sys


logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
logging.info("this is info")


def load_json(file: str = "config.json") -> dict:
    with open(file) as jf:
        configs = json.load(jf)
    return configs


def get_ref(template: dict, excel: dict) -> str:
    k_ = excel["RefGenome"]
    ref = template["def_parameters"]["RefGenome"][k_]
    return ref["ref-dir"]


def fastq_file(excel: dict, read_n: int) -> str:
    sample_name = excel["Sample_Name"]
    sample_number = excel["index"]
    lane_number = excel.get("Lane")
    if lane_number:
        file_name = (
            f"{sample_name}_S{sample_number}_L00{lane_number}_R{read_n}_001.fastq"
        )
    else:
        file_name = f"{sample_name}_S{sample_number}_R{read_n}_001.fastq"
    return file_name


def check_key(dct: dict, k: str, val: str) -> str:
    if k in dct.keys():
        dct[k] = val
        return dct
    else:
        raise KeyError


def normal_pipeline(template: dict, excel: dict, pipeline: str = "normal_pipeline"):
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "fastq-file1", fastq_file(excel, 1))
        cmd = check_key(cmd, "fastq-file2", fastq_file(excel, 2))
        cmd = check_key(cmd, "qc-coverage-region-1", excel["TargetRegions"])
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}",
            exc_info=True,
        )
        raise
        exit(1)
    except:
        logging.critical(f"Unexpected error: {sys.exc_info()[0]}")
        raise
        exit(1)
    return cmd


def tumor_alignment(template: dict, excel: dict, pipeline: str = "tumor_alignment"):
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "tumor-fastq1", fastq_file(excel, 1))
        cmd = check_key(cmd, "tumor-fastq2", fastq_file(excel, 2))
        cmd = check_key(cmd, "qc-coverage-region-1", excel["TargetRegions"])
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}",
            exc_info=True,
        )
        raise
        exit(1)
    except:
        logging.critical(f"Unexpected error: {sys.exc_info()[0]}")
        raise
        exit(1)
    return cmd


def tumor_variant(
    template: dict, excel: dict, tumor: dict, pipeline: str = "tumor_variant_call"
):
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "tumor-bam-input", f"{tumor['output-file-prefix']}.bam")
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}",
            exc_info=True,
        )
        raise
        exit(1)
    except:
        logging.critical(f"Unexpected error: {sys.exc_info()[0]}")
        raise
        exit(1)
    return cmd


def paired_variant(
    template: dict,
    excel: dict,
    normal_bam: str,
    tumor: dict,
    pipeline: str = "paired_variant_call",
):
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "bam-input", normal_bam)
        cmd = check_key(cmd, "tumor-bam-input", f"{tumor['output-file-prefix']}.bam")
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}",
            exc_info=True,
        )
        raise
        exit(1)
    except:
        logging.critical(f"Unexpected error: {sys.exc_info()[0]}")
        raise
        exit(1)
    return cmd

def dragen_cli(cmd:dict) -> str:
    default_str = " ".join(f"--{key} {val}" for (key, val) in cmd.items())
    final_str = f"dragen {default_str}"
    return final_str



class constructDragen(Flow):
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

        #  if it's "T" 1) run tumor allignment 2) run tumor variant call
        if excel.get("tumor/normal") == "T":
            logging.info(
                f"{excel.get('tumor/normal')}:preparing tumor alignment template"
            )
            # Todo:
            # define fastq1 & fastq2
            # define prefix rgid, rgism => rgid is sample id, placeholder idx1_idx2
            # tumor fast fastq1 and 2
            arg_strings = []
            cmd_d1 = tumor_alignment(self.profile, excel, "tumor_alignment")

            default_str1 = " ".join(f"--{key} {val}" for (key, val) in cmd_d1.items())
            final_str1 = f"dragen {default_str1}"
            arg_strings.append(final_str1)
            # 2. prepare tumor_variant_call_template
            # Todo:
            # define tumor bam input => outpufile-prefix.bam (from previous run)
            # get defaults
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
            logging.info(f"{self.current_t}: preparing tumor alignment template")
            cmd_d1 = tumor_alignment(self.profile, excel, "tumor_alignment")

            final_str1 = dragen_cli(cmd_d1)
            arg_string.append(final_str1)
            # Todo:
            # define tumor bam input => tumor output prefix.bam
            # define bam-input  =noraml ouput prefix.bam prvious n1 run
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
