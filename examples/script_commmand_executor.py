from pipeshell import PipeShell, ScriptCommandExecutor, Base64CommandStager

PipeShell(ScriptCommandExecutor("./script.sh", Base64CommandStager()))
