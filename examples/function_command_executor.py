import subprocess
from pipeshell import PipeShell, FunctionCommandExecutor, Base64CommandStager

# Actual function (e.g. RCE exploit) that is capable of executing command on target.
def execute(command: str) -> str:
    return subprocess.getoutput(command)

PipeShell(FunctionCommandExecutor(execute, Base64CommandStager()))
