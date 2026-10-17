"""``linecount``: um programa de linha de comando que segue as convenções que os outros programas esperam.

    linecount a.txt b.txt        conta linhas por arquivo
    cat a.txt | linecount -      lê da entrada padrão
    linecount --json *.txt       saída para máquinas
"""
import argparse
import json
import os
import signal
import sys

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_INTERRUPTED = 0, 1, 2, 130


def use_color(mode: str, stream) -> bool:
    """auto: cor só se a saída é um terminal E NO_COLOR não está definido; always/never mandam."""
    if mode == "always":
        return True
    if mode == "never" or "NO_COLOR" in os.environ:
        return False
    return stream.isatty()


def paint(text: str, code: str, enabled: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if enabled else text


def count_lines(name: str) -> int:
    stream = sys.stdin.buffer if name == "-" else open(name, "rb")
    try:
        return sum(1 for _ in stream)
    finally:
        if name != "-":
            stream.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="linecount", description="Conta as linhas de arquivos.")
    parser.add_argument("files", nargs="*", default=["-"], metavar="ARQUIVO", help="arquivos (use - para a entrada padrão)")
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    parser.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    parser.add_argument("-q", "--quiet", action="store_true", help="não imprime os arquivos com erro")
    args = parser.parse_args(argv)                                  # uso incorreto: argparse sai com 2

    color = use_color(args.color, sys.stdout)
    results, failed = {}, 0
    for name in args.files:
        try:
            results[name] = count_lines(name)
        except OSError as error:
            failed += 1
            if not args.quiet:
                print(paint(f"linecount: {name}: {error.strerror}", "31", use_color(args.color, sys.stderr)), file=sys.stderr)

    if args.json:
        print(json.dumps({"files": results, "total": sum(results.values())}, ensure_ascii=False))
    else:
        for name, n in results.items():
            print(f"{paint(str(n), '32', color):>{8 if not color else 17}} {name}")
        if len(results) > 1:
            print(f"{sum(results.values()):>8} total")
    return EXIT_ERROR if failed else EXIT_OK


def run() -> None:
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(file=sys.stderr)                                       # nova linha depois do ^C
        sys.exit(EXIT_INTERRUPTED)                                   # 128 + SIGINT(2): a convenção do shell
    except BrokenPipeError:                                          # `linecount ... | head -1`: o leitor fechou o cano
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())      # evita um erro ao esvaziar o stdout na saída
        sys.exit(0)


if __name__ == "__main__":
    run()
