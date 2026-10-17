"""O que está rodando: versão, build, GIL, JIT, opções."""
import platform
import sys
import sysconfig

print(sys.version)
print(platform.python_implementation(), sys.implementation.cache_tag, sys.implementation.version[:3])
print("GIL ativo:", sys._is_gil_enabled(), "| build free-threaded:", bool(sysconfig.get_config_var("Py_GIL_DISABLED")))
print("compilador:", platform.python_compiler())
jit = sys._jit
print("JIT: disponível =", jit.is_available(), "| habilitado =", jit.is_enabled(), "| ativo =", jit.is_active())
print("debug build:", bool(sysconfig.get_config_var("Py_DEBUG")), "| -O:", sys.flags.optimize)
print("limite de recursão:", sys.getrecursionlimit(), "| int máx de dígitos str:", sys.get_int_max_str_digits())
print("opções -X:", dict(sys._xoptions))
print("float:", sys.float_info.max, sys.float_info.dig, "| hash:", sys.hash_info.width, "bits")
print("byteorder:", sys.byteorder, "| maxsize:", sys.maxsize)
