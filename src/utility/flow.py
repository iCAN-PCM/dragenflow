from abc import ABC, abstractmethod
from pathlib import Path
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
    def execute_flow(command: str, **kwargs) -> tuple:
        """
        Helper function applicable to all Flow (this is optional)
        """
        base_cmd = kwargs.get("base_cmd")
        command = command
        wd_path = kwargs.get("wd_path", Path.cwd())
        if base_cmd == "echo":
            arg_list = ["echo", command]
            output = subprocess.run(
                arg_list,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                shell=False,
                cwd=wd_path,
            )
        else:
            arg_list = shlex.split(command)
            output = subprocess.run(
                arg_list,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                cwd=wd_path,
                shell=False,
            )
        return (output, arg_list)


class Flow(ABC):
    @abstractmethod
    def constructor(self, data: dict):
        pass
