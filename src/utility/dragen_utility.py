import csv
import errno
import json
import os
from pathlib import Path
import shutil
from typing import List


def custom_sort(val: str) -> float:

    rank = 0.0
    if len(str(val)) > 1:
        if val[0] == "N":
            rank = float(val[-1]) - 0.5
        if val[0] == "T":
            rank = float(val[-1])

    return rank


def script_path(filename: str) -> str:
    """
    A convenience function to get the absolute path to a file in this
    This allows the file to be launched from any
    directory.
    """

    filepath = os.path.join(os.path.dirname(__file__))
    config_path = os.path.join(filepath, "..")
    return os.path.join(config_path, filename)


def load_json(file: str = "config.json") -> dict:
    with open(file) as jf:
        configs = json.load(jf)
    return configs


def get_ref(excel: dict, template: dict) -> str:
    k_ = excel["RefGenome"]
    ref = template["ref_parameters"]["RefGenome"][k_]
    return ref["ref-dir"]


def set_fileprefix(excel: dict) -> str:
    sample_id = excel["SampleID"] if excel.get("SampleID") else excel["Sample_ID"]
    return sample_id


def set_rgid(excel: dict) -> str:
    sample_sheet_path = excel["file_path"]
    flow_cell_id = get_flow_cell(sample_sheet_path)
    if excel.get("Lane"):
        flow_cell_id = f"{flow_cell_id}-{excel.get('Lane')}"
    return f"{flow_cell_id}-{excel['row_index']}"


def set_rgism(excel: dict) -> str:
    rgism = excel["SampleID"] if excel.get("SampleID") else excel["Sample_ID"]
    return rgism


def create_fastq_dir(excel: list, dry_run: bool = False) -> List[dict]:
    for row in excel:
        if row["pipeline"].lower() != "dragen":
            continue
        path = Path(row["file_path"]).absolute()
        sample_id = row["SampleID"] if row.get("SampleID") else row["Sample_ID"]
        new_path = path.parent / row["Sample_Project"] / sample_id
        if not dry_run:
            new_path.mkdir(exist_ok=True)
        row["fastq_dir"] = new_path
        row["dry_run"] = dry_run
    return excel


def fastq_file(excel: dict, read_n: int, copy_file: bool = True) -> str:

    sample_name = excel["Sample_Name"]
    sample_number = excel["row_index"]
    lane_number = excel.get("Lane")
    if lane_number:
        file_name = (
            f"{sample_name}_S{sample_number}_L00{lane_number}_R{read_n}_001.fastq.gz"
        )
    else:
        file_name = f"{sample_name}_S{sample_number}_R{read_n}_001.fastq.gz"
    if copy_file:
        move_fast_q(excel, file_name)
    return file_name


def move_fast_q(excel: dict, fastq_f: str) -> None:

    sample_sheet_path = Path(excel["file_path"]).absolute().parent
    path_to_fastq = sample_sheet_path / excel["Sample_Project"] / fastq_f
    destination_of_fastq = Path(excel["fastq_dir"])
    final_fastq_path = destination_of_fastq / fastq_f
    if not excel["dry_run"]:
        if path_to_fastq.exists():
            # in case if file already exist in destination
            if not final_fastq_path.exists():
                shutil.move(str(path_to_fastq), str(destination_of_fastq))
        elif not final_fastq_path.exists():
            print("")
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), str(path_to_fastq)
            )


def check_key(dct: dict, k: str, val: str) -> dict:
    if k in dct.keys():
        dct[k] = val
        return dct
    else:
        raise KeyError


def dragen_cli(cmd: dict, excel: dict, postf: str = "") -> str:
    default_str = " ".join(f"--{key} {val}" for (key, val) in cmd.items())
    if postf:
        postf = "-" + postf
    final_str = f"grun.py -n dragen-{excel['Sample_Name']}{postf} -L logs -q  dragen.q -c 'dragen {default_str}'"  # noqa: E501, B950
    return final_str


def infer_pipeline(pipeline: str) -> str:
    str_list = pipeline.split("_")
    return str_list[0]


def get_flow_cell(path: str) -> str:
    path = os.path.abspath(path)
    split_path = path.split("/")
    flow_cell = split_path[-3]
    flow_cell_id = flow_cell.split("_")[-1]
    return flow_cell_id


def basic_reader(path: str) -> list:

    with open(path, newline="", encoding="utf-8") as inf:
        reader = csv.DictReader(inf)

        return list(reader)


def trim_options(excel: dict, template: dict) -> str:
    # check if adaptertrim exist in sample sheet
    if excel.get("AdapterTrim"):
        if excel["AdapterTrim"] == "truseq" or excel["AdapterTrim"] == "nextera":
            return template["adapters"][excel["AdapterTrim"]]
        elif excel["AdapterTrim"].startswith("/"):
            return excel["AdapterTrim"]
        else:
            raise ValueError(
                f"Cannot retrieve adapters for value: {excel['AdapterTrim']}"
            )
    else:
        return ""


def file_parse(path: str, head_identifier="Lane") -> List[dict]:
    # change the variable name
    with open(path, newline="", encoding="utf-8") as inf:
        reader = csv.reader(inf)
        # find header row
        for row in reader:
            if row[0].startswith(head_identifier):
                # if "" not in row:
                fieldnames = row
                break
        else:
            # oops, *only* rows with empty cells found
            raise ValueError("Unable to determine header row")

        # if need to rewind, switch to DictReader, skip past header: inf.seek(0)
        reader = csv.DictReader(inf, fieldnames)
        # Add the index before sorting
        row_index = 1
        reader = [val for val in reader]
        for row in reader:
            # convert Sample_ID into SampleID
            if row.get("Sample_ID"):
                row["SampleID"] = row.pop("Sample_ID")
            row["row_index"] = row_index
            row["file_path"] = path
            row_index += 1

        # Remove the pipeline that is not dragen
        # This must of be done before setting index, we need to preserve index
        reader = [row for row in reader if row["pipeline"] == "dragen"]

        return reader


def run_type(excel: List[dict]) -> List[dict]:

    for dt in excel:
        if (
            dt["Is_tumor"] == "0"
            or dt["Is_tumor"] == ""
            or dt["Is_tumor"].lower() == "no"
        ):
            dt["run_type"] = "germline"
        elif len(dt["Is_tumor"]) >= 1 and dt["matching_normal_sample"] == "":
            dt["run_type"] = "somatic_single"
        elif len(dt["Is_tumor"]) >= 1 and dt["matching_normal_sample"] != "":
            sample_id = dt["matching_normal_sample"]
            sample_project = dt["Sample_Project"]
            if check_sample(excel, sample_id, sample_project):
                dt["run_type"] = "somatic_paired"
            else:
                raise RuntimeError(
                    f"sample id {sample_id} doesn't exist at {dt['row_index']}"
                )
        else:
            raise ValueError(f"invalid entry at index {dt['row_index']}")
    return excel


def check_sample(excel: List[dict], sample_id: str, sample_project: str) -> bool:
    for dt in excel:
        if dt["SampleID"] == sample_id and dt["Sample_Project"] == sample_project:
            return True
        else:
            continue
    return False


def sort_list(excel: List[dict], sorting_col: str = "run_type") -> List[dict]:
    sorted_list = sorted(
        excel,
        key=lambda row: 1 if row[sorting_col] == "germline" else 0,
        reverse=True,
    )
    return sorted_list
