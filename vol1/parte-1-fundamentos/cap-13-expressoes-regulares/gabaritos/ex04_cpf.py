"""Gabarito 4: CPF = regex de formato + aritmética em código."""
import re

CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}")
# Para varrer texto livre, sem pegar pedaço de número maior
CPF_IN_TEXT = re.compile(
    r"(?<!\d)(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?!\d)")


def _check_digits(first_nine: str) -> str:
    digits = [int(c) for c in first_nine]
    for _ in range(2):
        weights = range(len(digits) + 1, 1, -1)
        total = sum(d * w for d, w in zip(digits, weights))
        digits.append(total * 10 % 11 % 10)   # 10 vira 0
    return "".join(map(str, digits[-2:]))


def is_valid_cpf(value: str) -> bool:
    if not CPF.fullmatch(value):
        return False
    digits = re.sub(r"\D", "", value)
    if len(set(digits)) == 1:
        return False
    return _check_digits(digits[:9]) == digits[9:]


def mask_cpfs(text: str) -> str:
    def mask(m: re.Match) -> str:
        if not is_valid_cpf(m[0]):
            return m[0]
        return f"***.***.***-{m[0][-2:]}"

    return CPF_IN_TEXT.sub(mask, text)
