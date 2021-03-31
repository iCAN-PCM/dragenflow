from flow import Flow
import json
import logging
from string import Formatter

logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
logging.info("this is info")


def load_json(file: str = "config.json") -> dict:
    with open(file) as jf:
        configs = json.load(jf)
    return configs

def get_ref(template:dict,data:dict) -> str:
    k_ = data['RefGenome']
    ref = template['def_parameters']['RefGenome'][k_]
    return ref['ref-dir']


def fastq_file(data: dict, read_n: int) -> str:
    sample_name = data["Sample_Name"]
    sample_number = data["index"]
    lane_number = data.get("Lane")
    if lane_number:
        file_name = (
            f"{sample_name}_S{sample_number}_L00{lane_number}_R{read_n}_001.fastq"
        )
    else:
        file_name = f"{sample_name}_S{sample_number}_R{read_n}_001.fastq"
    return file_name


class constructDragen(Flow):
    def __init__(self):
        self.n = 1
        self.current_n = f"N{self.n}"
        self.current_t = f"T{self.n}"
        self.last_fastq_file = ""
        self.last_bam_file = ""
        self.args = load_json()["profile1"]

    def constructor(self, data: dict) -> [str]:
        # "N" (or empty), it triggers normal_pipeline_template
        print(data.get("tumor/normal"))
        if data.get("tumor/normal") == "N":
            logging.info(f"{data.get('tumor/normal')}: executing normal_pipeline")

            # Get defaults
            default_dict = self.args["normal_pipeline"]
            try:
                default_dict["fastq-file1"], default_dict["fastq-file2"] = (
                    fastq_file(data, 1),
                    fastq_file(data, 2),
                )
            except KeyError as e:
                logging.error(
                    f"Failed to infer fastq file at index {data.get('index')}", exc_info=True
                )
            # should exist 
            default_dict["qc-coverage-region-1"] = data["TargetRegions"]
            default_dict["ref-dir"] = get_ref(self.args,data)

            default_str = " ".join(
                f"--{key} {val}" for (key, val) in default_dict.items()
            )
            final_str = f"dragen {default_str}" 

            return [final_str]

        #  if it's "T" 
        # run tumor allignment
        # run tumor variant call
        if data.get("tumor/normal") == "T":
            logging.info(
                f"{data.get('tumor/normal')}:preparing tumor alignment template"
            )
            # Todo:
            # define fastq1 & fastq2
            # define prefix rgid, rgism => rgid is sample id, placeholder idx1_idx2
            # tumor fast fastq1 and 2
            arg_strings = []
            # print(data)
            args = load_json()
            # 1. prepare tumor_alignment template
            # Get defaults

            default_dict1 = self.args["tumor_alignment"]
            try:
                default_dict1["tumor-fastq1"], default_dict1["tumor-fastq2"] = (
                    fastq_file(data, 1),
                    fastq_file(data, 2),
                )
            except KeyError as e:
                logging.error(
                    f"Failed to infer fastq file at index {data.get('index')}", exc_info=True
                )
            # should exist
            default_dict1['qc-coverage-region-1'] = data['TargetRegions']
            default_dict1["ref-dir"] = get_ref(self.args,data)
            default_str1 = " ".join(
                f"--{key} {val}" for (key, val) in default_dict1.items()
            )
            final_str1 = f"dragen {default_str1}"
            arg_strings.append(final_str1)
            # 2. prepare tumor_variant_call_template
            # Todo:
            # define tumor bam input => outpufile-prefix.bam (from previous run)
            # get defaults
            default_dict2 = self.args["tumor_variant_call"]
            default_dict2["ref-dir"] = get_ref(self.args,data)
            default_dict2[
                "tumor-bam-input"
            ] = f"{default_dict1['output-file-prefix']}.bam"
            logging.info("preparing tumor variant call template")
            default_str2 = " ".join(
                f"--{key} {val}" for (key, val) in default_dict1.items()
            )

            final_str2 = f"dragen {default_str2}"
            arg_strings.append(final_str2)
            return arg_strings

        # if it's N1
        # run normal pipeline
        if data.get("tumor/normal") == self.current_n:
            # Todo:
            # define prefix
            # define RGID, RGSM
            default_dict = self.args["normal_pipeline"]
            default_dict["ref-dir"] = get_ref(self.args,data)
            logging.info(f"{self.current_n}: preparing normal_pipeline")
            default_str = " ".join(
                f"--{key} {val}" for (key, val) in default_dict.items()
            )
            final_str = f"dragen {default_str}"
            self.last_bam_file = f"{default_dict['output-file-prefix']}.bam"
            return [final_str]

        # if it's T1
        # run tumor alignment
        # paried
        if data.get("tumor/normal") == self.current_t:
            # Todo:
            # define prefic
            # define fastq1 fastq2
            # define rgid rgsm
            arg_string = []
            default_dict1 = self.args["tumor_alignment"]
            default_dict1["ref-dir"] = get_ref(self.args,data)
            logging.info(f"{self.current_t}: preparing tumor alignment template")
            try:
                default_dict1["tumor-fastq1"], default_dict1["tumor-fastq2"] = (
                    fastq_file(data, 1),
                    fastq_file(data, 2),
                )
            except KeyError as e:
                logging.error(
                    f"Failed to infer fastq file at index {data.get('index')}", exc_info=True
                )
            # some more code
            default_str1 = " ".join(
                f"--{key} {val}" for (key, val) in default_dict1.items()
            )
            final_str1 = f"dragen {default_str1}"
            arg_string.append(final_str1)
            # Todo:
            # define tumor bam input => tumor output prefix.bam
            # define bam-input  =noraml ouput prefix.bam prvious n1 run
            # define prefix = needs to be dicided
            default_dict2 = self.args["paired_variant_call"]
            default_dict2["ref-dir"] = get_ref(self.args,data)
            logging.info(f"{self.current_t}: preparing paired varaint call template")
            default_dict2['bam-input'] = self.last_bam_file
            default_dict2['tumor-bam-input'] = f"{default_dict1['output-file-prefix']}.bam"
            default_str2 = " ".join(
                f"--{key} {val}" for (key, val) in default_dict2.items()
            )
            final_str2 = f"dragen {default_str2}"
            arg_string.append(final_str2)

            self.n += 1
            self.current_n = f"N{self.n}"
            self.current_t = f"T{self.n}"
            logging.info(f"counter incremented to:{self.n}")
            logging.info(self.current_n)
            logging.info(self.current_t)
            return arg_string
