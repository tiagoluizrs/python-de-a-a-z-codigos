"""Gabarito do exercício 1: mini "wc" com argparse."""
import argparse
import sys
from pathlib import Path


def count_text(text: str) -> tuple[int, int, int]:
    # count("\n") é o que o wc de verdade faz para "linhas"
    return text.count("\n"), len(text.split()), len(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wc", description="mini wc")
    parser.add_argument("files", nargs="+")
    parser.add_argument("-l", "--lines", action="store_true")
    parser.add_argument("-w", "--words", action="store_true")
    parser.add_argument("-c", "--chars", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Sem flags, mostramos tudo
    wanted = (args.lines, args.words, args.chars)
    if not any(wanted):
        wanted = (True, True, True)
    status = 0
    for name in args.files:
        path = Path(name)
        if not path.is_file():
            print(f"wc: {name}: not found", file=sys.stderr)
            status = 1
            continue
        counts = count_text(path.read_text(encoding="utf-8"))
        shown = [str(n) for n, want in zip(counts, wanted) if want]
        print(" ".join(shown), name)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
