"""A árvore de exceções embutidas (as 71 classes do 3.15)."""


def tree(cls, depth=0, lines=None):
    lines = [] if lines is None else lines
    lines.append("  " * depth + cls.__name__)
    for sub in sorted(cls.__subclasses__(), key=lambda c: c.__name__):
        if sub.__module__ == "builtins":
            tree(sub, depth + 1, lines)
    return lines


lines = tree(BaseException)
print(len(lines), "classes embutidas")

# Só os dois primeiros níveis
print("\n".join(line for line in lines if line.count("  ") <= 1))

# As famílias que você mais captura
for family in (LookupError, ArithmeticError, OSError):
    names = [c.__name__ for c in family.__subclasses__()
             if c.__module__ == "builtins"]
    print(f"{family.__name__}: {names}")

print(issubclass(KeyboardInterrupt, Exception),
      issubclass(SystemExit, Exception),
      issubclass(GeneratorExit, Exception))
import asyncio
print(issubclass(asyncio.CancelledError, Exception))   # False: BaseException
print(OSError is IOError, OSError is EnvironmentError)
