"""re.DEBUG mostra como o padrão foi interpretado."""
import re

re.compile(r"a+?b|[0-9]{2}", re.DEBUG)
print("-----")
re.compile(r"(?>a+)b|c++", re.DEBUG)
