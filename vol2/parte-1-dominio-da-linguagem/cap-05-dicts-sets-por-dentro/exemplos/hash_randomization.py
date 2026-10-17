"""Roda subprocessos com PYTHONHASHSEED diferentes para ver o efeito."""
import os
import subprocess
import sys

CODE = (
    "words = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']\n"
    "print(hash('abc') % 1000, hash(42), hash((1, 'a')) % 1000)\n"
    "print(list(set(words)))\n"
    "print(list(dict.fromkeys(words)))\n"
    "print(list(set(range(5))))\n"
)


def run(seed):
    env = dict(os.environ)
    if seed is None:
        env.pop("PYTHONHASHSEED", None)
    else:
        env["PYTHONHASHSEED"] = seed
    out = subprocess.run([sys.executable, "-c", CODE], env=env,
                         capture_output=True, text=True, check=True)
    return out.stdout.strip().splitlines()


for seed in ("0", "0", "1", "2", None, None):
    label = "aleatoria" if seed is None else f"seed={seed}"
    lines = run(seed)
    print(f"--- {label}")
    print("\n".join(lines))
