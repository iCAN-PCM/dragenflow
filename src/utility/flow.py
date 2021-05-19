from __future__ import annotations

from abc import ABC, abstractmethod
import copy
import shlex
import subprocess
from typing import List


class FlowConstructor:
    """
    The FlowConstructor define the interface necessary to construct various
    piplines/flow
    """

    def __init__(self, flow: Flow, data: dict) -> None:
        self._flow = flow
        self.data = data

    @property
    def flow(self) -> Flow:
        """
        flow keeps a reference to one of the Flow objects. flow doesn't
        know the concrete class of Flow but should work with all Flow through
        flow interface.
        """
        return self._flow

    @flow.setter
    def flow(self, flow: Flow) -> None:
        self._flow = flow

    def construct_flow(self) -> str:
        """
        FlowConstructor delegates main task to the Flow object instead of
        implementing multiple version of the task on its own.
        """

        data = copy.deepcopy(self.data)
        constructed = self._flow.constructor(data)
        return constructed

    def execute_flow(self, **kwargs) -> List[tuple]:
        """
        Helper function applicable to all Flow (this is optional)
        """
        base_cmd = kwargs.get("base_cmd")
        list_output = []
        data = copy.deepcopy(self.data)
        bash_strings = self._flow.constructor(data)
        # arg_list = bash_string.split(" ")
        for string in bash_strings:
            # arg_list = shlex.split(string)
            if base_cmd == "echo":
                arg_list = ["echo", string]
                output = subprocess.run(
                    arg_list,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                    shell=False,
                )
            else:
                arg_list = shlex.split(string)
                output = subprocess.run(
                    arg_list,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                )
            # list_output.append(output)
            # print(output)
            # print("--------")
            list_output.append((output.returncode, output.stdout))
        return list_output


class Flow(ABC):
    @abstractmethod
    def constructor(self, data: dict):
        pass
