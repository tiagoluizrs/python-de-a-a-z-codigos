"""Gabarito 1: classificar comandos com match."""


def parse_command(line: str) -> tuple:
    match line.split():
        case []:
            return ("noop",)
        case ["quit" | "exit"]:
            return ("quit",)
        # 'as' captura qual alternativa do OR casou
        case ["go", ("north" | "south" | "east" | "west") as way]:
            return ("move", way)
        # qualquer outro "go ..." (sem direção ou inválida)
        case ["go", *_]:
            return ("error", "go where?")
        # *items captura 0 ou mais; o guard exige pelo menos um
        case ["pick", *items] if items:
            return ("pick", " ".join(items))
        case [first, *_]:
            return ("unknown", first)
