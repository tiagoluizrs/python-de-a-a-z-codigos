"""Tour pela sintaxe: literais, classes, âncoras, quantificadores."""
import re

# Strings brutas: sem r"", \b vira backspace (caractere 8)
print(len("\b"), len(r"\b"))
print(re.findall("\bpy\b", "py is fun"))     # []
print(re.findall(r"\bpy\b", "py is fun"))    # ['py']

# Classes e atalhos
print(re.findall(r"[aeiou]", "regular expression"))
print(re.findall(r"[^aeiou\s]+", "regular expression"))
print(re.findall(r"[a-c-]", "a-d-c"))        # hífen literal no fim
print(re.findall(r"\d{2,3}", "1 22 333 4444"))

# Âncoras
text = "line one\nline two\n"
print(re.findall(r"^line", text))
print(re.findall(r"^line", text, re.MULTILINE))
print(re.search(r"one$", "one\n"))           # $ casa antes do \n final
print(re.search(r"one\Z", "one\n"))          # \Z não
print(re.search(r"one\z", "one"))            # \z: sinônimo (3.14)

# Greedy x lazy x possessivo
html = "<b>bold</b> and <i>it</i>"
print(re.findall(r"<.+>", html))
print(re.findall(r"<.+?>", html))
print(re.findall(r"<[^>]+>", html))
print(re.search(r"<.++>", html))            # possessivo: engole tudo
print(re.search(r"<.++>x", "<abc>"))         # e não devolve nada

# Alternância: a primeira alternativa que casa vence
print(re.match(r"cat|category", "category").group())
print(re.match(r"category|cat", "category").group())
print(re.match(r"cat(?:egory)?", "category").group())
