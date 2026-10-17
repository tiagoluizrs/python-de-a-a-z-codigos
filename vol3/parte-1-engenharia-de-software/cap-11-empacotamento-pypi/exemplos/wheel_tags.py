"""Os rótulos (tags) de uma wheel: python, ABI e plataforma."""
from packaging import tags, utils

supported = list(tags.sys_tags())
print(f"esta máquina aceita {len(supported)} rótulos; os 4 mais específicos e os 2 mais genéricos:")
for tag in supported[:4] + supported[-2:]:
    print("  ", tag)

print()
for name in ["requests-2.34.2-py3-none-any.whl", "numpy-2.4.0-cp315-cp315-win_amd64.whl",
             "numpy-2.4.0-cp315-cp315-manylinux_2_28_x86_64.whl", "cryptography-46.0.0-cp311-abi3-win_amd64.whl",
             "six-1.17.0-py2.py3-none-any.whl", "tomli-2.1.0-py3-none-any.whl"]:
    dist, version, build, wheel_tags = utils.parse_wheel_filename(name)
    ok = any(tag in supported for tag in wheel_tags)
    print(f"{name:<58} instala aqui: {ok}")

print()
print("anatomia:  {nome}-{versão}[-{build}]-{python}-{abi}-{plataforma}.whl")
print("  py3-none-any      -> Python puro: serve a qualquer sistema")
print("  cp315-cp315-win_amd64 -> compilada para CPython 3.15, Windows de 64 bits")
print("  cp311-abi3-...    -> API estável (abi3): uma wheel serve do 3.11 em diante")
sdist = utils.parse_sdist_filename("greeter_demo-0.3.0.tar.gz")
print("sdist:", sdist)
