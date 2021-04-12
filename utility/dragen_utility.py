import json
import logging


def custom_sort(val: str) -> int:

    if len(str(val)) > 1:
        if val[0] == "N":
            return val[-1]
        if val[0] == "T":
            return val[-1]
    else:
        return 0


def load_json(file: str = "config.json") -> dict:
    with open(file) as jf:
        configs = json.load(jf)
    return configs


def get_ref(template: dict, excel: dict) -> str:
    k_ = excel["RefGenome"]
    ref = template["def_parameters"]["RefGenome"][k_]
    return ref["ref-dir"]


def set_fileprefix(excel: dict) -> str:
    prefix = "samplename"
    return prefix


def set_rgid(excel: dict) -> str:
    sample_id = excel["Sample_Name"]
    return sample_id


def set_rgism(excel: dict) -> str:
    rgism = excel["SampleID"]
    return rgism


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


def normal_pipeline(
    template: dict, excel: dict, pipeline: str = "normal_pipeline"
) -> dict:
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "fastq-file1", fastq_file(excel, 1))
        cmd = check_key(cmd, "fastq-file2", fastq_file(excel, 2))
        cmd = check_key(cmd, "output-file-prefix", set_fileprefix(excel))
        cmd = check_key(cmd, "qc-coverage-region-1", excel["TargetRegions"])
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}", exc_info=True
        )
        raise
        exit(1)

    return cmd


def tumor_alignment(
    template: dict, excel: dict, pipeline: str = "tumor_alignment"
) -> dict:
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "tumor-fastq1", fastq_file(excel, 1))
        cmd = check_key(cmd, "tumor-fastq2", fastq_file(excel, 2))
        cmd = check_key(cmd, "output-file-prefix", set_fileprefix(excel))
        cmd = check_key(cmd, "qc-coverage-region-1", excel["TargetRegions"])
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}", exc_info=True
        )
        raise
        exit(1)
    return cmd


def tumor_variant(
    template: dict, excel: dict, tumor: dict, pipeline: str = "tumor_variant_call"
) -> dict:
    try:
        cmd = template[pipeline]
        cmd = check_key(cmd, "tumor-bam-input", f"{tumor['output-file-prefix']}.bam")
        cmd = check_key(cmd, "output-file-prefix", set_fileprefix(excel))
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}", exc_info=True
        )
        raise
        exit(1)

    return cmd


def paired_variant(
    template: dict,
    excel: dict,
    normal_bam: str,
    tumor: dict,
    pipeline: str = "paired_variant_call",
) -> dict:
    try:
        cmd = template[pipeline]
        # tumor bam input => tumor output prefix.bam
        # bam-input  => noraml ouput prefix.bam from previous n1 run
        cmd = check_key(cmd, "bam-input", normal_bam)
        cmd = check_key(cmd, "tumor-bam-input", f"{tumor['output-file-prefix']}.bam")
        cmd = check_key(cmd, "ref-dir", get_ref(template, excel))
    except KeyError as e:
        logging.critical(
            f"Failed to parse dictionary {excel.get('index')} \n {e}", exc_info=True
        )
        raise
        exit(1)

    return cmd


def dragen_cli(cmd: dict) -> str:
    default_str = " ".join(f"--{key} {val}" for (key, val) in cmd.items())
    final_str = f"dragen {default_str}"
    return final_str
