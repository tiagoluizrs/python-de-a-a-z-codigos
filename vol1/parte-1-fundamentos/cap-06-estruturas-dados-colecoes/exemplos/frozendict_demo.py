"""frozendict (novo no 3.15, PEP 814)."""
import collections.abc as abc
import json
import pickle
import sys

settings = frozendict(host="localhost", port=80)
print(settings, type(settings))
print(isinstance(settings, dict), isinstance(settings, abc.Mapping),
      isinstance(settings, abc.MutableMapping))
print(frozendict.__mro__)
print(settings == {"host": "localhost", "port": 80})
print(settings == frozendict(port=80, host="localhost"))
try:
    settings["port"] = 8080
except TypeError as error:
    print("TypeError:", error)
print([m for m in dir(settings) if not m.startswith("_")])

# Hasheável se chaves e valores forem hasheáveis
cache = {settings: "ok"}
print(cache[frozendict(host="localhost", port=80)])
print(hash(settings) == hash(frozenset(settings.items())))
try:
    hash(frozendict(a=[1]))
except TypeError as error:
    print("TypeError:", error)

# "Alterar" = criar outro
updated = settings | {"port": 8080}
print(updated, settings)
print(type(settings | {"a": 1}), type({"a": 1} | settings))
print(settings.copy() is settings)
print(dict(settings), {**settings, "debug": True})
print(pickle.loads(pickle.dumps(settings)) == settings)
print(frozendict.fromkeys("ab", 0))
print(sys.getsizeof(settings), sys.getsizeof(dict(settings)))
try:
    print(json.dumps(settings))
except TypeError as error:
    print("TypeError:", error)
print(json.dumps(dict(settings)))
