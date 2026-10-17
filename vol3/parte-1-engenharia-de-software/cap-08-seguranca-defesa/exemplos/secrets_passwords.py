"""Senhas, tokens e comparação em tempo constante."""
import hashlib
import hmac
import random
import secrets
import time

# sha256 é RÁPIDO por projeto: ótimo para integridade, péssimo para senhas
start = time.perf_counter()
n = 200_000
for _ in range(n):
    hashlib.sha256(b"senha123").digest()
per_hash = (time.perf_counter() - start) / n
print(f"sha256: {per_hash * 1e9:.0f} ns por tentativa -> {1 / per_hash:,.0f} tentativas/s em um núcleo")

# Algoritmos LENTOS de propósito (e com memória): scrypt, pbkdf2
start = time.perf_counter()
digest = hashlib.scrypt(b"senha123", salt=b"0123456789abcdef", n=2**14, r=8, p=1, dklen=32)
scrypt_ms = (time.perf_counter() - start) * 1e3
start = time.perf_counter()
hashlib.pbkdf2_hmac("sha256", b"senha123", b"0123456789abcdef", 600_000)
pbkdf2_ms = (time.perf_counter() - start) * 1e3
print(f"scrypt (n=2^14): {scrypt_ms:.0f} ms | pbkdf2-sha256 (600 mil iterações): {pbkdf2_ms:.0f} ms por tentativa")
print(f"razão scrypt/sha256: {scrypt_ms * 1e6 / (per_hash * 1e9):,.0f}x mais lento para quem ataca")

# O salt faz o MESMO texto gerar hashes diferentes (e inutiliza tabelas pré-calculadas)
salt_a, salt_b = secrets.token_bytes(16), secrets.token_bytes(16)
hash_a = hashlib.scrypt(b"mesma", salt=salt_a, n=2**10, r=8, p=1)
hash_b = hashlib.scrypt(b"mesma", salt=salt_b, n=2**10, r=8, p=1)
print("mesma senha, salts diferentes -> hashes iguais?", hash_a == hash_b)

# random é previsível; secrets usa a fonte do sistema operacional
random.seed(42)
first = [random.randint(0, 9) for _ in range(6)]
random.seed(42)
print("random com a mesma semente repete:", first == [random.randint(0, 9) for _ in range(6)])
print("secrets nunca repete:", secrets.token_urlsafe(16), secrets.token_urlsafe(16))
print("tamanhos: token_bytes(16) =", len(secrets.token_bytes(16)), "| token_hex(16) =", len(secrets.token_hex(16)))

# Comparar segredos em tempo constante
token = secrets.token_hex(16)
print("compare_digest:", hmac.compare_digest(token, token), hmac.compare_digest(token, "x" * 32))

# HMAC: autenticar uma mensagem com uma chave secreta
key = secrets.token_bytes(32)
message = b"pedido=42&valor=100"
signature = hmac.new(key, message, hashlib.sha256).hexdigest()
tampered = hmac.new(key, b"pedido=42&valor=999", hashlib.sha256).hexdigest()
print("assinatura confere:", hmac.compare_digest(signature, hmac.new(key, message, hashlib.sha256).hexdigest()),
      "| mensagem adulterada confere:", hmac.compare_digest(signature, tampered))
