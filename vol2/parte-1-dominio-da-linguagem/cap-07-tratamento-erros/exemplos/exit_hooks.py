"""Exceção não tratada: código de saída, excepthook e threads."""
import gc
import subprocess
import sys
import threading


def run(code):
    return subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True)


result = run("raise ValueError('x')")
print("não tratada:", result.returncode, "|",
      result.stderr.strip().splitlines()[-1])
print("sys.exit(3):", run("import sys; sys.exit(3)").returncode)
result = run("raise SystemExit('mensagem final')")
print("SystemExit(str):", result.returncode, repr(result.stderr))
print("python -O ignora assert:",
      run("assert False; print('rodou')").stdout.strip() or "erro",
      "|", subprocess.run([sys.executable, "-O", "-c",
                           "assert False; print('rodou')"],
                          capture_output=True, text=True).stdout.strip())

hook = (
    "import sys\n"
    "def hook(tp, val, tb):\n"
    "    print('hook:', tp.__name__, val)\n"
    "sys.excepthook = hook\n"
    "raise ValueError('boom')\n"
)
result = run(hook)
print(result.stdout.strip(), "| código:", result.returncode)

# Exceções em threads não derrubam o programa: vão para threading.excepthook
seen = []
threading.excepthook = lambda args: seen.append(
    (args.exc_type.__name__, str(args.exc_value)))
thread = threading.Thread(target=lambda: 1 / 0)
thread.start()
thread.join()
threading.excepthook = threading.__excepthook__
print("threading.excepthook:", seen)


# Exceções em __del__ são "inlevantáveis": vão para sys.unraisablehook
class Noisy:
    def __del__(self):
        raise ValueError("no __del__")


captured = []
sys.unraisablehook = lambda info: captured.append(str(info.exc_value))
Noisy()
gc.collect()
sys.unraisablehook = sys.__unraisablehook__
print("unraisable:", captured)
