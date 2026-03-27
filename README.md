# PipeShell

*PipeShell* is a FIFO-based pseudo-shell built for constrained environments where traditional reverse shells are ineffective—such as systems with strict egress filtering, hardened firewalls, or limited remote code execution capabilities.

It converts blind or semi-interactive command execution into a practical, interactive shell experience—without relying on inbound or outbound network connections.

When the target environment permits, PipeShell can also upgrade the pseudo-shell into a fully interactive TTY session.

---
### :warning: DISCLAIMER  
This project is intended **for educational, research, and authorized security testing purposes only**.  
**Do not use this code on systems you do not own or have explicit permission to test.**  
The author is **not responsible** for any damage or misuse.

---

## 🧠 Concept

PipeShell abuses Unix IPC primitives (`mkfifo`) to emulate a persistent shell:

1. Create named pipes in shared memory (`/dev/shm`)
2. Spawn a detached shell bound to the pipe
3. Feed commands into the pipe
4. Poll output from another pipe
5. Encode everything with base64 to avoid parsing issues

This results in a fully interactive loop over stateless command execution.

## 📦 Installation

```shell
python3 -m venv .venv && source .venv/bin/activate && pip3 install git+https://github.com/magicrc/pipeshell.git
```

## 🚀 Usage

```python
#!/usr/bin/python3
import subprocess
from pipeshell import PipeShell, FunctionCommandExecutor, Base64CommandStager

# Actual function (e.g. RCE exploit) that is capable of executing command on target.
def execute(command: str) -> str:
    return subprocess.getoutput(command)

PipeShell(FunctionCommandExecutor(execute, Base64CommandStager()))
```

## 💻 Example session
```
┌──(.venv)─(magicrc㉿perun)-[~/code/pipeshell/examples]
└─$ python3 ./function_command_executor.py            
[+] Establishing IPC on target...OK
[+] Session ID: 97715
[+] Shell PID: 1585507

┌──(pipesh)─(magicrc㉿perun)
└─$ ls -la
total 20
drwxrwxr-x 2 magicrc magicrc 4096 Mar 30 08:52 .
drwxrwxr-x 7 magicrc magicrc 4096 Mar 30 08:44 ..
-rw-rw-r-- 1 magicrc magicrc  325 Mar 28 09:52 function_command_executor.py
-rw-rw-r-- 1 magicrc magicrc  148 Mar 30 08:49 script_commmand_executor.py
-rwxrwxr-x 1 magicrc magicrc   31 Mar 30 08:49 script.sh
┌──(pipesh)─(magicrc㉿perun)
└─$ /help
/help      Show this help menu
/upgrade   Upgrade to a fully interactive TTY
/exit      Exit and clean up session
┌──(pipesh)─(magicrc㉿perun)
└─$ /upgrade

[+] Spawning interactive TTY...
┌──(.venv)(magicrc㉿perun)-[~/code/pipeshell/examples]
└─$ sudo su
sudo su
[sudo] password for magicrc:

┌──(root㉿perun)-[/home/magicrc/code/pipeshell/examples]
└─# id
id
uid=0(root) gid=0(root) groups=0(root)
                                                                                
┌──(root㉿perun)-[/home/magicrc/code/pipeshell/examples]
└─# exit
exit

┌──(.venv)(magicrc㉿perun)-[~/code/pipeshell/examples]
└─$ exit
[+] TTY session closed, returning to PipeShell
┌──(pipesh)─(magicrc㉿perun)
└─$
```
