from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from utility.dragen_utility import (
    fastq_file,
    get_ref,
    set_fileprefix,
    set_rgid,
    set_rgism,
)


class Pipeline(ABC):
    def __init__(self, excel: dict, template: dict, seq_pipeline: str) -> None:
        self.ex_dict = excel
        self.tpl_dict = template
        self.seq_pipeline = seq_pipeline
        self.arg_registry = {
            "fastq-file1": fastq_file(self.ex_dict, 1),
            "fastq-file2": fastq_file(self.ex_dict, 2),
            "tumor-fastq1": fastq_file(self.ex_dict, 1),
            "tumor-fastq2": fastq_file(self.ex_dict, 2),
            "output-file-prefix": set_fileprefix(self.ex_dict),
            "qc-coverage-region-1": self.ex_dict["TargetRegions"],
            "ref-dir": get_ref(self.ex_dict, self.tpl_dict),
            "RGID": set_rgid(self.ex_dict),
            "RGSM": set_rgism(self.ex_dict),
            "RGID-tumor": set_rgid(self.ex_dict),
            "RGSM-tumor": set_rgism(self.ex_dict),
        }

    @property
    def parent(self) -> Pipeline:
        return self._parent

    @parent.setter
    def parent(self, parent: Pipeline) -> None:
        self._parent = parent

    @abstractmethod
    def construct_pipeline(self) -> dict:
        pass


class CompositePipeline(Pipeline):
    def __init__(self) -> None:
        self._children: List[Pipeline] = []

    def add(self, pipeline: Pipeline) -> None:
        self._children.append(pipeline)
        pipeline.parent = self

    def remove(self, pipeline: Pipeline) -> None:
        self._children.remove(pipeline)
        pipeline.parent = None

    def is_composite(self) -> bool:
        return True

    def construct_pipeline(self) -> dict:
        finale_pipeline = {}
        for child in self._children:
            pipe_dict = child.construct_pipeline()
            finale_pipeline.update(pipe_dict)

        return finale_pipeline


class BasePipeline(Pipeline):
    def construct_pipeline(self) -> dict:
        try:
            cmd_dict = self.tpl_dict[self.seq_pipeline]
        except KeyError as e:
            print(self.ex_dict)
            print(self.tpl_dict)
            raise e

        param_list = [i for i in cmd_dict if str(cmd_dict[i]).startswith("{")]
        for val in param_list:
            try:
                cmd_dict[val] = self.arg_registry.get(val)
            except KeyError:
                print(f"missing key {val}: in registry")
                continue
        assert type(cmd_dict) == dict
        return cmd_dict


class TumorVariantPipeline(Pipeline):
    def __init__(self, tumor: dict) -> None:
        self.tumor = tumor

    def construct_pipeline(self) -> dict:

        cmd_dict = {"tumor-bam-input": f"{self.tumor['output-file-prefix']}.bam"}

        assert type(cmd_dict) == dict
        return cmd_dict


class PairedVariantPipeline(Pipeline):
    def __init__(self, normal_bam: str, tumor: dict) -> None:
        self.tumor = tumor
        self.normal_bam = normal_bam

    def construct_pipeline(self) -> dict:
        cmd_dict = {}
        cmd_dict["bam-input"] = self.normal_bam
        cmd_dict["tumor-bam-input"] = f"{self.tumor['output-file-prefix']}.bam"
        assert type(cmd_dict) == dict
        return cmd_dict
