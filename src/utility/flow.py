from abc import ABC, abstractmethod
import shlex
import subprocess
from typing import List


class FlowConstructor:
    """
    The FlowConstructor define the interface necessary to construct various
    piplines/flow
    """

    def __init__(self, flow) -> None:
        self._flow = flow

    @property
    def flow(self):
        """
        flow keeps a reference to one of the Flow objects. flow doesn't
        know the concrete class of Flow but should work with all Flow through
        flow interface.
        """
        return self._flow

    @flow.setter
    def flow(self, flow) -> None:
        self._flow = flow

    def construct_flow(self, data: dict) -> List[str]:
        """
        FlowConstructor delegates main task to the Flow object instead of
        implementing multiple version of the task on its own.
        """

        constructed = self._flow.constructor(data)
        return constructed

    @staticmethod
    def execute_flow(**kwargs) -> List[tuple]:
        """
        Helper function applicable to all Flow (this is optional)
        """
        base_cmd = kwargs.get("base_cmd")
        command_list = kwargs.get("cmd_list")
        list_output = []
        for path, string in command_list:
            if base_cmd == "echo":
                arg_list = ["echo", string]
                output = subprocess.run(
                    arg_list,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                    shell=False,
                    cwd=path,
                )
            else:
                arg_list = shlex.split(string)
                output = subprocess.run(
                    arg_list, universal_newlines=True, stdout=subprocess.PIPE, cwd=path
                )
            list_output.append((output.returncode, output.stdout))
        return list_output


class Flow(ABC):
    @abstractmethod
    def constructor(self, data: dict):
        pass
