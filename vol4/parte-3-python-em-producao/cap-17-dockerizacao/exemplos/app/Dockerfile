# syntax=docker/dockerfile:1
# O Dockerfile de produção: duas etapas, dependências em camada própria, usuário sem privilégios.

FROM ghcr.io/astral-sh/uv:0.13.0 AS uv

# ---- etapa 1: constrói o ambiente virtual (com compilador, cache e tudo que NÃO vai para produção) ----
FROM python:3.15-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
COPY --from=uv /uv /bin/uv
WORKDIR /app
# 1) só as dependências: esta camada só é refeita quando pyproject.toml ou uv.lock mudam
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev
# 2) o código: muda toda hora, mas a camada acima continua em cache
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable

# ---- etapa 2: a imagem final só leva o ambiente pronto ----
FROM python:3.15-slim AS runtime
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app --no-create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8000
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]
CMD ["shop-api"]
