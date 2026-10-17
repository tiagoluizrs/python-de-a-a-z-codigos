"""Os erros de sistema: OSError, as subclasses e o errno."""
import errno
import tempfile
from pathlib import Path

print([c.__name__ for c in OSError.__subclasses__()
       if c.__module__ == "builtins"])
print(FileNotFoundError.__mro__)

try:
    open("/nao/existe/arquivo.txt")
except OSError as error:
    print(type(error).__name__, error.errno, error.strerror,
          error.filename, errno.errorcode[error.errno])

with tempfile.TemporaryDirectory() as tmp:
    target = Path(tmp) / "x.txt"
    target.write_text("ok")
    try:
        open(target, "x")                     # modo "x": falha se existir
    except FileExistsError as error:
        print(type(error).__name__, error.errno, errno.errorcode[error.errno])

# Prefira a subclasse a comparar errno
try:
    Path("/nao/existe").read_text()
except FileNotFoundError:
    print("a subclasse diz tudo")
except OSError as error:
    print("outro erro de SO:", error.errno)
