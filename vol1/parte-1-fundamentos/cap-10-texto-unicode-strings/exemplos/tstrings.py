"""t-strings (PEP 750, Python 3.14): interpolação sem virar str."""
import html
import sqlite3
from string.templatelib import Interpolation, Template, convert

user = "Ana"
price = 9.5
tpl = t"Olá, {user!r:>8}! Total: {price:.2f}"

print(type(tpl).__name__, isinstance(tpl, str))
print(tpl.strings)
print(tpl.values)
print(tpl.interpolations[0])
print(list(tpl))
# nada foi formatado: conversão e especificação ficam com o processador
for item in tpl.interpolations:
    print(item.value, item.expression, item.conversion,
          repr(item.format_spec))

# renderizador que reproduz o comportamento de uma f-string
def render_like_fstring(template: Template) -> str:
    parts = []
    for item in template:
        if isinstance(item, Interpolation):
            value = convert(item.value, item.conversion)
            parts.append(format(value, item.format_spec))
        else:
            parts.append(item)
    return "".join(parts)


print(render_like_fstring(tpl))
print(f"Olá, {user!r:>8}! Total: {price:.2f}")


# 1) HTML seguro: o texto estático é confiável, os valores são escapados
def html_render(template: Template) -> str:
    parts = []
    for item in template:
        if isinstance(item, Interpolation):
            value = format(convert(item.value, item.conversion),
                           item.format_spec)
            parts.append(html.escape(value))
        else:
            parts.append(item)
    return "".join(parts)


comment = '<script>alert("x")</script>'
print(html_render(t"<p>{comment}</p>"))
print(f"<p>{comment}</p>")                       # a f-string não protege


# 2) SQL parametrizado: valores viram "?" e vão separados
def sql(template: Template) -> tuple[str, tuple]:
    text = []
    for item in template:
        text.append("?" if isinstance(item, Interpolation) else item)
    return "".join(text), template.values


db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, age INTEGER)")
db.execute("INSERT INTO users VALUES ('Ana', 31), ('Bob', 25)")
evil = "x' OR '1'='1"
query, params = sql(t"SELECT name FROM users WHERE name = {evil}")
print(query, params, db.execute(query, params).fetchall())
query, params = sql(t"SELECT name FROM users WHERE age > {20}")
print(query, params, db.execute(query, params).fetchall())
unsafe = f"SELECT name FROM users WHERE name = '{evil}'"
print(unsafe, db.execute(unsafe).fetchall())      # vazou tudo

# construir e concatenar templates
base = Template("Total: ", Interpolation(42, "total"))
print((base + t" ({user})").values)
try:
    t"a" + "b"
except TypeError as exc:
    print("TypeError:", exc)
