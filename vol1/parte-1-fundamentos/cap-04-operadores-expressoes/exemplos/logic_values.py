"""and / or / not devolvem OPERANDOS, não apenas True/False."""
print(0 or "default")        # default
print("" or [] or None)      # None  (devolve o último, se todos forem falsos)
print("hi" and 42)           # 42    (devolve o último, se todos forem verdadeiros)
print(0 and 1 / 0)           # 0     (curto-circuito: 1 / 0 nem executa)
print(not 0, not "x", not [])  # True False True: not SEMPRE devolve bool

# Armadilha do "x or default": valores falsos legítimos são descartados
timeout = 0
print(timeout or 30)         # 30  <- o usuário pediu 0!
print(timeout if timeout is not None else 30)   # 0

# Guarda: só acessa o atributo se o objeto existir
user = None
print(user and user.name)    # None

data = [3, 7, 9]
print(all(n > 0 for n in data), any(n > 8 for n in data))   # True True
print(all([]), any([]))      # True False  (casos vazios)
