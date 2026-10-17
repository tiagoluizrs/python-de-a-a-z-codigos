"""Exercício 4: armazenar e verificar senhas."""


def hash_password(password, *, n=2**14, r=8, p=1):
    """Devolve o texto ``"scrypt$<n>$<r>$<p>$<salt em hex>$<hash em hex>"``.

    * ``salt``: 16 bytes de ``secrets.token_bytes`` (um novo a cada chamada);
    * hash: ``hashlib.scrypt(senha em UTF-8, salt=..., n=..., r=..., p=...,
      dklen=32)``;
    * duas chamadas com a mesma senha dão textos DIFERENTES."""
    raise NotImplementedError


def verify_password(password, stored):
    """``True`` se ``password`` confere com ``stored`` (formato acima, com os
    parâmetros lidos do próprio texto). Compare em TEMPO CONSTANTE
    (``hmac.compare_digest``). Texto malformado (partes faltando, não numérico,
    hex inválido, algoritmo diferente de scrypt) devolve ``False``, sem levantar."""
    raise NotImplementedError


def needs_rehash(stored, *, n=2**14, r=8, p=1):
    """``True`` se ``stored`` foi gerado com parâmetros MAIS FRACOS (``n``, ``r`` ou
    ``p`` menores) que os pedidos, ou se está malformado: sinal de que o hash
    deve ser refeito no próximo login bem-sucedido."""
    raise NotImplementedError
