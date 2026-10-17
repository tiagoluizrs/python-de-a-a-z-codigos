"""Exemplos realistas: comandos, JSON, rotas, AST."""


def parse_command(line: str) -> str:
    match line.split():
        case ["quit" | "exit"]:
            return "bye"
        case ["go", ("north" | "south" | "east" | "west") as way]:
            return f"going {way}"
        case ["go", *_]:
            return "go where? (north, south, east, west)"
        case ["pick", item]:
            return f"picked {item}"
        case ["pick", *items] if items:
            return f"picked {' '.join(items)} (all of them)"
        case []:
            return "type something"
        case [cmd, *_]:
            return f"unknown command: {cmd}"


for text in ("go north", "go up", "go", "pick sword", "pick a b",
             "exit", "", "dance now"):
    print(f"{text!r:14} -> {parse_command(text)}")

print()


# JSON validando dados
def describe_user(data):
    match data:
        case {"name": str(name), "age": int(age)} if age >= 18:
            return f"{name} (adult)"
        case {"name": str(name), "age": int()}:
            return f"{name} (minor)"
        case {"name": str(name), "emails": [first, *_]}:
            return f"{name} <{first}>"
        case {"name": str()}:
            return "incomplete"
        case _:
            return "invalid"


samples = [
    {"name": "Ana", "age": 30},
    {"name": "Bia", "age": 12},
    {"name": "Caio", "emails": ["c@x.org", "d@x.org"]},
    {"name": "Dan"},
    {"name": 7, "age": 1},
    ["not", "a", "dict"],
]
for sample in samples:
    print(describe_user(sample))

print()


# Roteamento simples
def route(method: str, path: str) -> str:
    match method, path.strip("/").split("/"):
        case "GET", [""]:
            return "home"
        case "GET", ["users"]:
            return "list users"
        case "GET", ["users", user_id] if user_id.isdigit():
            return f"show user {user_id}"
        case "POST", ["users"]:
            return "create user"
        case ("PUT" | "PATCH"), ["users", user_id]:
            return f"update user {user_id}"
        case _, ["users", *_]:
            return "405 method not allowed"
        case _:
            return "404"


for m, p in [("GET", "/"), ("GET", "/users"), ("GET", "/users/42"),
             ("GET", "/users/x"), ("PATCH", "/users/7"),
             ("DELETE", "/users"), ("GET", "/nope")]:
    print(m, p, "->", route(m, p))

print()


# Mini AST em tuplas
def evaluate(node):
    match node:
        case int() | float():
            return node
        case ("+", left, right):
            return evaluate(left) + evaluate(right)
        case ("*", left, right):
            return evaluate(left) * evaluate(right)
        case ("-", operand):
            return -evaluate(operand)
        case _:
            raise ValueError(f"invalid node: {node!r}")


tree = ("+", 2, ("*", 3, ("-", 4)))
print(evaluate(tree))
try:
    evaluate(("/", 1, 2))
except ValueError as exc:
    print(exc)

print()


# FizzBuzz com match
def fizzbuzz(n):
    match n % 3, n % 5:
        case 0, 0:
            return "FizzBuzz"
        case 0, _:
            return "Fizz"
        case _, 0:
            return "Buzz"
        case _:
            return str(n)


print(" ".join(fizzbuzz(n) for n in range(1, 16)))

# 3.15: sinal + em literais
match 5:
    case +5:
        print("unary plus literal (3.15)")
match -2.5:
    case -2.5:
        print("unary minus literal")
