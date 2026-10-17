# Python de A a Z: códigos

Códigos, exercícios e gabaritos do livro **Python de A a Z** (Tiago Silva).
Todo o código foi executado no **Python 3.15**.

## Estrutura

O repositório é dividido nos **cinco volumes** do livro (`vol1` a `vol5`); dentro de cada volume há uma pasta por parte e, dentro dela, uma pasta por capítulo. **Cada capítulo é um projeto
independente**, com o próprio `pyproject.toml`, ambiente virtual e testes:

```
volN/parte-N-nome/cap-NN-slug/
├── pyproject.toml   dependências deste capítulo
├── exemplos/        código mostrado no livro (executável)
├── exercicios/      esqueletos para você completar
├── gabaritos/       soluções comentadas
└── tests/           testes que corrigem o seu exercício
```

## Como usar

Instale o [uv](https://docs.astral.sh/uv/) (veja o Capítulo 2 do livro) e entre na pasta do capítulo:

```bash
cd vol1/parte-1-fundamentos/cap-01-ecossistema-python
uv sync                                # cria o ambiente (Python 3.15)
uv run python exemplos/runtime_info.py
uv run pytest                          # corrige os seus exercícios
```

Para validar os gabaritos: `CHECK_GABARITOS=1 uv run pytest`.

## Volumes

| Pasta | Conteúdo | Capítulos (a numeração recomeça em cada volume) |
|-------|----------|-----------|
| `vol1` | Parte 1: Fundamentos | 1 a 14 |
| `vol2` | Parte 1: Domínio da linguagem | 1 a 19 |
| `vol3` | Partes 1 e 2: Engenharia de software e concorrência | 1 a 19 |
| `vol4` | Partes 1, 2 e 3: Persistência, mundo real e produção | 1 a 21 |
| `vol5` | Partes 1 a 4: Padrões de projeto | 1 a 32 |
