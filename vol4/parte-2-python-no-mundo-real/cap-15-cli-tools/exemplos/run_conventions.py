"""Roda o ``linecount`` como outro programa o faria (subprocess) e mostra as convenções em ação."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).parent
work = Path(tempfile.mkdtemp(prefix="cli-cap67-"))
(work / "a.txt").write_text("um\ndois\ntrês\n", encoding="utf-8")
(work / "b.txt").write_text("x\ny\n", encoding="utf-8")


def run(*args, stdin=None, env_extra=None):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", **(env_extra or {})}
    env.pop("NO_COLOR", None) if not env_extra or "NO_COLOR" not in env_extra else None
    return subprocess.run([sys.executable, str(HERE / "linecount.py"), *args], input=stdin, capture_output=True, text=True, cwd=work, env=env, encoding="utf-8")


def show(title, proc):
    print(f"\n$ {title}")
    for line in proc.stdout.splitlines():
        print("   stdout:", repr(line))
    for line in proc.stderr.splitlines():
        print("   stderr:", repr(line))
    print("   código de saída:", proc.returncode)


# 1. resultado em stdout, erro em stderr, e o código de saída diz quem venceu
show("linecount a.txt b.txt", run("a.txt", "b.txt"))
show("linecount a.txt falta.txt", run("a.txt", "falta.txt"))
show("linecount -q a.txt falta.txt", run("-q", "a.txt", "falta.txt"))

# 2. uso incorreto: código 2 (o argparse) e uma mensagem que sugere a correção (3.15)
show("linecount --colour never a.txt", run("--colour", "never", "a.txt"))
show("linecount --color alway a.txt", run("--color", "alway", "a.txt"))

# 3. entrada padrão: o programa funciona em um pipe
show("echo 'a\\nb\\nc' | linecount -", run("-", stdin="a\nb\nc\n"))
show("echo ... | linecount (sem argumento = stdin)", run(stdin="1\n2\n"))

# 4. saída para máquinas: JSON válido e estável
proc = run("--json", "a.txt", "b.txt")
print("\n$ linecount --json a.txt b.txt ->", json.loads(proc.stdout))

# 5. cores: automáticas só em terminal; NO_COLOR e --color decidem
print("\ncores (o subprocess NÃO é um terminal, então 'auto' fica sem cor):")
print("   auto           :", repr(run("a.txt").stdout.splitlines()[0]))
print("   --color always :", repr(run("--color", "always", "a.txt").stdout.splitlines()[0]))
print("   NO_COLOR=1 + always ... always vence?", repr(run("--color", "always", "a.txt", env_extra={"NO_COLOR": "1"}).stdout.splitlines()[0]))
print("   NO_COLOR=1 + auto:", repr(run("a.txt", env_extra={"NO_COLOR": "1"}).stdout.splitlines()[0]))

# 6. | head: o leitor fecha o cano antes do fim (BrokenPipeError)
big = work / "big.txt"
big.write_text("linha\n" * 2_000_000, encoding="utf-8")
cmd = f'"{sys.executable}" "{HERE / "linecount.py"}" --json big.txt big.txt big.txt | "{sys.executable}" -c "import sys; sys.stdin.readline()"'
start = time.perf_counter()
piped = subprocess.run(cmd, shell=True, cwd=work, capture_output=True, text=True)
print(f"\ncano fechado cedo: código {piped.returncode}, stderr: {piped.stderr!r} ({(time.perf_counter() - start) * 1e3:.0f} ms)")

# 7. Ctrl+C: o código 130 (128 + SIGINT) é a convenção; simulamos o KeyboardInterrupt, que é o que o Ctrl+C levanta
code = "import linecount\n\ndef boom(argv=None):\n    raise KeyboardInterrupt\n\nlinecount.main = boom\nlinecount.run()"
interrupted = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True)
print(f"\nKeyboardInterrupt dentro do programa: código de saída {interrupted.returncode}, traceback no stderr? {'Traceback' in interrupted.stderr}")
