from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class Commands(ABC):
    @property
    def parent(self) -> Commands:
        return self._parent

    @parent.setter
    def parent(self, parent: Commands) -> None:
        self._parent = parent

    @abstractmethod
    def construct_commands(self) -> dict:
        pass


class CompositeCommands(Commands):
    def __init__(self) -> None:
        self._children: List[Commands] = []

    def add(self, Commands: Commands) -> None:
        self._children.append(Commands)
        Commands.parent = self

    def remove(self, Commands: Commands) -> None:
        self._children.remove(Commands)
        Commands.parent = None

    def is_composite(self) -> bool:
        return True

    def construct_commands(self) -> dict:
        finale_commands = {}
        for child in self._children:
            pipe_dict = child.construct_commands()
            finale_commands.update(pipe_dict)

        return finale_commands
