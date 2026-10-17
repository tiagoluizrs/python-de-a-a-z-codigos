"""os, sys, shutil, subprocess, platform, atexit, signal."""
import atexit
import os
import platform
import shutil
import signal
import subprocess
import sys

print(sys.platform, platform.python_implementation(), sys.version_info[:2])
print(os.name, os.cpu_count() is not None)
print(os.environ.get("NOPE_VAR", "<padrão>"))
print(shutil.which("python") is not None)

# subprocess seguro: lista de argumentos, sem shell
done = subprocess.run(
    [sys.executable, "-c", "print('hello from child')"],
    capture_output=True, text=True, check=True, timeout=30,
)
print(done.returncode, done.stdout.strip())

# check=True levanta CalledProcessError
try:
    subprocess.run([sys.executable, "-c", "raise SystemExit(3)"], check=True)
except subprocess.CalledProcessError as exc:
    print("falhou com código", exc.returncode)

# Injeção de shell: com shell=True a entrada vira comando
user_input = "x & echo INJECTED"
line = f'"{sys.executable}" -c "print(1)" {user_input}'
out = subprocess.run(line, shell=True, capture_output=True, text=True)
print("shell=True executou o extra:", "INJECTED" in out.stdout)

code = "import sys; print(sys.argv[1:])"
out = subprocess.run([sys.executable, "-c", code, user_input],
                     capture_output=True, text=True)
print("lista de args trata como texto:", out.stdout.strip())

atexit.register(lambda: print("encerrando (atexit)"))
print(signal.SIGINT.value, signal.SIGINT.name)
