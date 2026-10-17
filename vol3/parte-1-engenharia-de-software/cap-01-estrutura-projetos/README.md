# cap-01-estrutura-projetos

Projeto-exemplo do capítulo 1: um pacote **instalável** com layout `src/`, ponto de entrada de linha
de comando, `__main__.py`, API pública explícita e testes. A pasta é independente dos outros capítulos.

```bash
uv sync                       # cria o ambiente e instala o pacote em modo editável
uv run inventory --help       # script de console definido em [project.scripts]
uv run python -m inventory --help
uv run pytest                 # testes do projeto + correção dos exercícios
```

```text
cap-01-estrutura-projetos/
├── pyproject.toml            # metadados, dependências, scripts, build backend
├── README.md
├── src/
│   └── inventory/            # o pacote (nome de import)
│       ├── __init__.py       # API pública e __version__
│       ├── __main__.py       # python -m inventory
│       ├── cli.py            # interface de linha de comando
│       ├── core.py           # regras de negócio (sem I/O)
│       ├── storage.py        # persistência (I/O)
│       └── _util.py          # detalhe interno (prefixo _)
├── tests/                    # fora do pacote
├── exemplos/                 # scripts do capítulo
├── exercicios/               # esqueletos
└── gabaritos/                # soluções
```

Para validar os gabaritos: `CHECK_GABARITOS=1 uv run pytest`.
