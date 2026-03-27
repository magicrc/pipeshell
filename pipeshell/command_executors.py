from abc import ABC, abstractmethod
from .command_stagers import CommandStager, PassThruCommandStager
from collections.abc import Callable
import subprocess

class CommandExecutor(ABC):
    def __init__(self, command_stager: CommandStager | None = None):
        self.__command_stager = command_stager or PassThruCommandStager()

    def execute(self, command: str) -> str:
        return self._execute(self.__command_stager.stage(command))

    @abstractmethod
    def _execute(self, command: str) -> str:
        raise NotImplementedError

class LocalCommandExecutor(CommandExecutor):
    def _execute(self, command: str) -> str:
        return subprocess.getoutput(command)

class ScriptCommandExecutor(CommandExecutor):
    def __init__(self, path: str, command_stager: CommandStager = PassThruCommandStager()):
        super().__init__(command_stager)
        self.__path = path

    def _execute(self, command: str) -> str:
        return subprocess.getoutput(f"{self.__path} '{command}'")

class FunctionCommandExecutor(CommandExecutor):
    def __init__(self, function: Callable[[str], str], command_stager: CommandStager = PassThruCommandStager()):
        super().__init__(command_stager)
        self.__function = function

    def _execute(self, command: str) -> str:
        return self.__function(command)
