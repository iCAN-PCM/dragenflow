from __future__ import annotations

from abc import ABC, abstractmethod
import copy
import shlex
import subprocess


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
        constructed_str = self._flow.constructor(data)
        return constructed_str

    def execute_flow(self) -> list:
        """
        Helper function applicable to all Flow (this is optional)
        """
        list_output = []
        data = copy.deepcopy(self.data)
        bash_strings = self._flow.constructor(data)
        # arg_list = bash_string.split(" ")
        for string in bash_strings:
            arg_list = shlex.split(string)
            output = subprocess.run(
                arg_list,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                shell=False,
            )
            list_output.append(output)
            print(output)
            print("--------")
        return list_output


class Flow(ABC):
    @abstractmethod
    def constructor(self, data: dict):
        pass
