"""Configuração comum dos exemplos: o DSN vem do ambiente (Capítulo 12 do Volume 3), com padrão para o compose."""
import os

DSN = os.environ.get("PG_DSN", "postgresql://postgres:postgres@localhost:55432/postgres")
