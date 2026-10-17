"""Um módulo de configuração: o singleton mais simples do Python. O corpo roda UMA vez, no primeiro import."""
print("  [app_settings] carregando (isto só aparece no primeiro import)")

DEBUG = False
TIMEOUT = 5.0
VALUES: dict = {}


def configure(**options):
    VALUES.update(options)
