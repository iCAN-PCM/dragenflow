import json


def custom_sort(val: str) -> int:

    if len(str(val)) > 1:
        if val[0] == "N":
            return int(val[-1])
        if val[0] == "T":
            return int(val[-1])
    else:
        return 0


def load_json(file: str = "config.json") -> dict:
    with open(file) as jf:
        configs = json.load(jf)
    return configs


def get_ref(excel: dict, template: dict) -> str:
    k_ = excel["RefGenome"]
    ref = template["ref_parameters"]["RefGenome"][k_]
    return ref["ref-dir"]


def set_fileprefix(excel: dict) -> str:
    prefix = "samplename"
    return prefix


def set_rgid(excel: dict) -> str:
    sample_sheet_path = excel["file_path"]
    flow_cell_id = get_flow_cell(sample_sheet_path)
    return flow_cell_id


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


def dragen_cli(cmd: dict) -> str:
    default_str = " ".join(f"--{key} {val}" for (key, val) in cmd.items())
    final_str = f"dragen {default_str}"
    return final_str


def infer_pipeline(pipeline: str) -> str:
    str_list = pipeline.split("_")
    return str_list[0]


def get_flow_cell(path: str) -> str:
    split_path = path.split("/")
    flow_cell = split_path[-4]
    flow_cell_id = flow_cell.split("_")[-1]
    return flow_cell_id
