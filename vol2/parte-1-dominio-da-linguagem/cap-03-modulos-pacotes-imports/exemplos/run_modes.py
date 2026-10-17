"""Tres formas de executar o mesmo codigo, e o que muda."""
import subprocess
import sys


def run(*args: str) -> None:
    print("$ python", *args)
    out = subprocess.run([sys.executable, *args], capture_output=True,
                         text=True)
    lines = (out.stdout + out.stderr).strip().splitlines()
    print("\n".join(lines[-3:]) if out.returncode else "\n".join(lines))
    print()


run("tooling/tool.py")          # script: sem pacote pai
run("-m", "tooling.tool")       # modulo dentro do pacote
run("-m", "tooling")            # usa tooling/__main__.py
