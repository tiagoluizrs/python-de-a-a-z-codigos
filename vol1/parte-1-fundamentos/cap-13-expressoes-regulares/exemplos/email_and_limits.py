"""O que regex NÃO resolve: parênteses, HTML, JSON, e-mail."""
import json
import re
from html.parser import HTMLParser

# 1. Aninhamento arbitrário não é regular
balanced = re.compile(r"\(\w*\)")
print(balanced.fullmatch("(a)"), balanced.fullmatch("((a))"))

def is_balanced(text: str) -> bool:
    depth = 0
    for ch in text:
        depth += (ch == "(") - (ch == ")")
        if depth < 0:
            return False
    return depth == 0

print(is_balanced("((a)(b))"), is_balanced("(()"))

# 2. HTML: a regex "óbvia" quebra com atributo contendo '>'
html = '<a title="x > y" href="/p">link</a>'
print(re.findall(r"<a [^>]*href=\"([^\"]+)\"", html))   # perde o href


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")

parser = LinkParser()
parser.feed(html)
print(parser.links)

# 3. JSON: regex acha "números", mas não sabe de contexto
doc = '{"price": 10, "note": "costs 20 or 30"}'
print(re.findall(r"\d+", doc), json.loads(doc)["price"])

# 4. E-mail: um padrão pragmático aceita lixo e rejeita válidos
simple = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
for addr in ("ana@example.com", "a..b@example.com", "ana@localhost",
             '"ana smith"@example.com', "ana@@example.com"):
    print(f"{addr:<26} {bool(simple.fullmatch(addr))}")
