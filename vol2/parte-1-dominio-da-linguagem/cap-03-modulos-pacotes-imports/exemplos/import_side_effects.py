"""Efeitos colaterais e singletons de modulo."""
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    sys.path.insert(0, tmp)
    # Um modulo executa UMA vez; todos os importadores veem o mesmo objeto
    (Path(tmp) / "counter_demo.py").write_text(
        "print('executando counter_demo')\n"
        "count = 0\n"
        "def hit():\n"
        "    global count\n"
        "    count += 1\n"
        "    return count\n")
    import counter_demo as a
    import counter_demo as b          # nao reexecuta
    from counter_demo import hit
    hit(); a.hit()
    print(a is b, b.count)            # True 2

    # Mesmo arquivo, nomes diferentes = modulos diferentes (cuidado!)
    sys.path.insert(0, str(Path(tmp).parent))
    other = __import__(Path(tmp).name + ".counter_demo", fromlist=["x"])
    print(other is a, other.count)    # False 0
    sys.path.remove(tmp)
    sys.path.pop(0)
