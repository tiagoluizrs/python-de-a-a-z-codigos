"""Gabarito do exercício 1."""
import argparse
import sys
from pathlib import Path


def main(argv, stdin=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = argparse.ArgumentParser(prog="wc")
    parser.add_argument("files", nargs="*", metavar="ARQUIVO")
    parser.add_argument("-l", dest="lines", action="store_true")
    parser.add_argument("-w", dest="words", action="store_true")
    parser.add_argument("-c", dest="bytes", action="store_true")
    args = parser.parse_args(argv)
    chosen = [flag for flag in ("lines", "words", "bytes") if getattr(args, flag)] or ["lines", "words", "bytes"]

    def counts(data: bytes) -> dict:
        return {"lines": data.count(b"\n"), "words": len(data.split()), "bytes": len(data)}

    def line(values: dict, name: str | None) -> str:
        text = " ".join(f"{values[k]:>7}" for k in chosen)
        return f"{text} {name}" if name else text

    code, total, shown = 0, {"lines": 0, "words": 0, "bytes": 0}, 0
    for name in args.files or ["-"]:
        if name == "-":
            data = (stdin.read() if stdin is not None else sys.stdin.buffer.read())
        else:
            try:
                data = Path(name).read_bytes()
            except OSError:
                print(f"wc: {name}: arquivo ou diretório inexistente", file=stderr)
                code = 1
                continue
        values = counts(data)
        for key in total:
            total[key] += values[key]
        shown += 1
        print(line(values, None if name == "-" else name), file=stdout)
    if shown > 1:
        print(line(total, "total"), file=stdout)
    return code
