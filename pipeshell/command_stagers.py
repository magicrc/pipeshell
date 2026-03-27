import base64

class CommandStager:
    def stage(self, command: str) -> str:
        raise NotImplementedError

class PassThruCommandStager(CommandStager):
    def stage(self, command: str) -> str:
        return command

class Base64CommandStager(CommandStager):
    def stage(self, command: str) -> str:
        return f"echo {base64.b64encode(command.encode("utf-8")).decode("utf-8")} | base64 -d | sh"
