"""Padrões de produção para o Brasil: valida FORMATO, não existência."""
import re

# Composição de padrões a partir de pedaços nomeados
DDD = r"[1-9]\d"
MOBILE = r"9\d{4}"
LANDLINE = r"[2-5]\d{3}"

PHONE = re.compile(
    rf"""
    ^(?:\+?55\s?)?             # código do país, opcional
    (?:\(?(?P<ddd>{DDD})\)?\s?)  # DDD, com ou sem parênteses
    (?P<prefix>{MOBILE}|{LANDLINE})
    -?(?P<suffix>\d{{4}})$
    """,
    re.VERBOSE,
)

CPF_FORMAT = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}")
CEP = re.compile(r"\d{5}-?\d{3}")
PLATE = re.compile(r"[A-Z]{3}-?\d{4}|[A-Z]{3}\d[A-Z]\d{2}")


def cpf_check_digits(first_nine: str) -> str:
    """Calcula os dois dígitos verificadores de um CPF."""
    digits = [int(c) for c in first_nine]
    for _ in range(2):
        weight = len(digits) + 1
        total = sum(d * w for d, w in zip(digits, range(weight, 1, -1)))
        digit = (total * 10) % 11 % 10
        digits.append(digit)
    return f"{digits[-2]}{digits[-1]}"


def is_valid_cpf(value: str) -> bool:
    """Formato (regex) + dígitos verificadores (código)."""
    if not CPF_FORMAT.fullmatch(value):
        return False
    digits = re.sub(r"\D", "", value)
    if len(set(digits)) == 1:        # 111.111.111-11 passa na conta
        return False
    return cpf_check_digits(digits[:9]) == digits[9:]


def normalize_phone(value: str) -> str | None:
    m = PHONE.fullmatch(value.strip())
    if m is None:
        return None
    return f"+55{m['ddd']}{m['prefix']}{m['suffix']}"


if __name__ == "__main__":
    for cpf in ("529.982.247-25", "52998224725", "529.982.247-26",
                "111.111.111-11", "529982.247-25"):
        print(f"{cpf:<16} {is_valid_cpf(cpf)}")
    for phone in ("(11) 98765-4321", "11987654321", "+55 11 3456-7890",
                  "(01) 98765-4321", "11 8765-4321"):
        print(f"{phone:<18} {normalize_phone(phone)}")
    for cep in ("01310-100", "01310100", "1310-100"):
        print(cep, bool(CEP.fullmatch(cep)))
    for plate in ("ABC-1234", "ABC1D23", "abc1d23", "AB1C234"):
        print(plate, bool(PLATE.fullmatch(plate)))
    print(CEP.fullmatch("00000-000") is not None, "<- formato ok, CEP inexistente")
