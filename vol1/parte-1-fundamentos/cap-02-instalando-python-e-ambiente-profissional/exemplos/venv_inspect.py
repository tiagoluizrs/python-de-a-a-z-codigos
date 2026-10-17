"""Descobre se o código está rodando dentro de um ambiente virtual."""
import sys
import sysconfig

in_venv = sys.prefix != sys.base_prefix

print(f"sys.prefix       : {sys.prefix}")
print(f"sys.base_prefix  : {sys.base_prefix}")
print(f"In virtual env?  : {in_venv}")
print(f"site-packages    : {sysconfig.get_paths()['purelib']}")
