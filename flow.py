from __future__ import annotations

import copy
import shlex
import subprocess
from abc import ABC, abstractmethod


class FlowConstructor:
    """
    The FlowConstructor define thes interface necessary to construct various
    piplines/flow
    """

    def __init__(self, flow: Flow, data: dict) -> None:
        self._flow = flow
        self.data = data

    @property
    def flow(self) -> Flow:
        """
        flow keeps a reference to one of the Flow objects. flow desn't
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
        result = self._flow.constructor(data)
        return result

    def execute_flow(self) -> None:
        data = copy.deepcopy(self.data)
        bash_string = self._flow.constructor(data)
        # arg_list = bash_string.split(" ")
        arg_list = shlex.split(bash_string)
        output = subprocess.run(arg_list)
        print("stdout:", output.stdout)
        print(output)
        print("--------")


class Flow(ABC):
    @abstractmethod
    def constructor(self):
        pass


class simpleFlow(Flow):
    """
    Simple test implimentation for abstract Flow
    """

    def constructor(self, data: dict) -> str:
        arg_string = " ".join(f"{key} {val}" for (key, val) in data.items())
        return arg_string
