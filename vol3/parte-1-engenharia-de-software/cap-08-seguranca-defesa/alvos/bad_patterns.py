"""Padrões inseguros comuns (NÃO execute): servem de alvo para o linter de segurança do ruff."""
import hashlib
import pickle
import random
import subprocess
import tempfile

import requests
import yaml

PASSWORD = "admin123"                                          # S105: senha no código


def risky(user_input, blob, url):
    eval(user_input)                                           # S307: eval
    exec(user_input)                                           # S102: exec
    pickle.loads(blob)                                         # S301: pickle
    subprocess.run(f"ls {user_input}", shell=True)             # S602: shell=True
    hashlib.md5(user_input.encode()).hexdigest()               # S324: hash fraco
    token = random.random()                                    # S311: random para segredo
    requests.get(url, verify=False)                            # S501: sem verificar TLS
    yaml.load(blob)                                            # S506: yaml.load inseguro
    path = tempfile.mktemp()                                   # S306: mktemp
    assert user_input, "obrigatório"                           # S101: assert
    try:
        pass
    except Exception:
        pass                                                   # S110: except/pass
    return token, path
