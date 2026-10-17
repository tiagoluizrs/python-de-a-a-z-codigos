# cap-10-documentacao

Projeto-exemplo do capítulo 10: um pacote pequeno (`shapes`) **bem documentado**, com docstrings
no estilo Google, *doctests* que rodam como testes, e documentação gerada com Sphinx.

## Instalação

```bash
uv sync
```

## Uso

```python
from shapes import Circle, Rectangle, total_area

print(total_area([Circle(1), Rectangle(2, 3)]))
```

## Documentação

```bash
uv run sphinx-build -b html docs docs/_build/html      # gera o HTML
uv run pdoc shapes -o docs/_pdoc                       # alternativa mais simples
uv run pytest                                          # testes e doctests
uv run interrogate -v src                              # cobertura de docstrings
```

## Licença

MIT.
