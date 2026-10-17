"""Mostra qual implementação e versão do Python está executando este código."""
import platform
import sys

print(f"Implementation : {platform.python_implementation()}")
print(f"Version        : {platform.python_version()}")
print(f"Compiler       : {platform.python_compiler()}")
print(f"Executable     : {sys.executable}")
print(f"Version tuple  : {tuple(sys.version_info)}")
print(f"Pointer size   : {sys.maxsize.bit_length() + 1} bits")
