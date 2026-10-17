"""Os passos de um import, feitos a mao."""
import importlib
import importlib.util
import sys

NAME = "colorsys"
print("1. no cache?", NAME in sys.modules)

spec = importlib.util.find_spec(NAME)          # 2. encontrar (finders)
print("2.", type(spec.loader).__name__, spec.origin.rsplit("\\", 1)[-1])
print("   cached:", spec.cached.rsplit("\\", 1)[-1])
print("   meta_path:", [f.__name__ for f in sys.meta_path])

mod = importlib.util.module_from_spec(spec)    # 3. criar o objeto
print("3. ainda fora do cache?", NAME in sys.modules)
sys.modules[NAME] = mod                        # (o import faz isso antes de executar)
spec.loader.exec_module(mod)                   # 4. carregar/executar
print("4.", mod.rgb_to_hsv(0, 1, 0))

print("5. vinculo:", importlib.import_module(NAME) is mod)
print("   import normal devolve o mesmo:", __import__(NAME) is mod)

# Um modulo ausente: find_spec devolve None (sem levantar erro)
print(importlib.util.find_spec("no_such_module_xyz"))
print(importlib.util.find_spec("json.decoder").name)  # importa o pai (json)
