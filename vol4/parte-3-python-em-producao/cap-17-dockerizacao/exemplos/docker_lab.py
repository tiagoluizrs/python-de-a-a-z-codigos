"""Um laboratório de Docker: constrói e mede as imagens do serviço ``app/`` (precisa do Docker rodando).

    python exemplos/docker_lab.py                # tudo
    python exemplos/docker_lab.py sizes signals  # só algumas seções (sizes, cache, signals, security, memory, secrets, compose)
"""
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

APP = Path(__file__).parent / "app"
VARIANTS = {"naive": "Dockerfile.naive", "slim": "Dockerfile.slim", "alpine": "Dockerfile.alpine", "good": "Dockerfile"}


def docker(*args, check=True, timeout=600):
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=check, timeout=timeout, encoding="utf-8")


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def build(variant: str, context: Path = APP, tag: str | None = None, no_cache=False) -> float:
    args = ["build", "-q", "-f", str(context / VARIANTS[variant]), "-t", tag or f"shop-api:{variant}"]
    if no_cache:
        args.append("--no-cache")
    _, seconds = timed(lambda: docker(*args, str(context), timeout=1800))
    return seconds


def image_size(tag: str) -> str:
    return docker("images", tag, "--format", "{{.Size}}").stdout.strip()


def run_container(tag: str, name: str, *extra) -> tuple[str, int]:
    docker("rm", "-f", name, check=False)
    docker("run", "-d", "--name", name, "-p", "127.0.0.1::8000", *extra, tag)
    port = int(docker("port", name, "8000/tcp").stdout.split(":")[-1])
    return name, port


def get(port: int, path: str, timeout=3):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as response:
        return json.loads(response.read())


def wait_ready(port: int, limit=30.0) -> float:
    start = time.perf_counter()
    while time.perf_counter() - start < limit:
        try:
            get(port, "/healthz", timeout=1)
            return time.perf_counter() - start
        except Exception:
            time.sleep(0.05)
    raise TimeoutError("o serviço não ficou pronto")


def cleanup(*names):
    for name in names:
        docker("rm", "-f", name, check=False)


def section_sizes():
    print("== TAMANHO E TEMPO DE CONSTRUÇÃO (do zero, sem cache) ==")
    for variant in VARIANTS:
        seconds = build(variant, no_cache=True)
        print(f"  {variant:<7} {image_size(f'shop-api:{variant}'):>8} | construção {seconds:6.1f} s | {VARIANTS[variant]}")
    print("  bases:", ", ".join(f"{t} {image_size(t)}" for t in ("python:3.15", "python:3.15-slim", "python:3.15-alpine")))


def section_cache():
    print("\n== O CACHE DE CAMADAS: reconstruir depois de mudar UMA linha do código ==")
    work = Path(tempfile.mkdtemp(prefix="docker-cache-"))
    ctx = work / "app"
    shutil.copytree(APP, ctx, ignore=shutil.ignore_patterns(".venv", "__pycache__"))
    for variant in ("naive", "good"):
        build(variant, ctx, tag=f"shop-cache:{variant}")                        # aquece o cache
        _, again = timed(lambda: build(variant, ctx, tag=f"shop-cache:{variant}"))
        server = ctx / "src" / "shop_api" / "server.py"
        server.write_text(server.read_text(encoding="utf-8") + f"\n# edição {variant}\n", encoding="utf-8")
        edit_seconds = build(variant, ctx, tag=f"shop-cache:{variant}")
        print(f"  {variant:<6} sem mudar nada {again:5.1f} s | depois de editar 1 linha do código {edit_seconds:5.1f} s")
    docker("rmi", "-f", "shop-cache:naive", "shop-cache:good", check=False)
    shutil.rmtree(work, ignore_errors=True)


def section_signals():
    print("\n== SINAIS: docker stop envia SIGTERM; quem é o PID 1? ==")
    for variant in ("naive", "slim", "good"):
        name, port = run_container(f"shop-api:{variant}", f"lab-{variant}")
        ready = wait_ready(port)
        info = get(port, "/")
        _, seconds = timed(lambda: docker("stop", name))
        code = docker("inspect", name, "--format", "{{.State.ExitCode}}").stdout.strip()
        logs = docker("logs", name).stdout + docker("logs", name).stderr
        print(f"  {variant:<6} pronto em {ready * 1e3:5.0f} ms | pid do Python = {info['pid']:>2} | docker stop {seconds:5.1f} s | código {code} | limpou? {'encerrado com limpeza' in logs}")
        cleanup(name)
    print("  (forma shell do CMD: o PID 1 é o `sh`, que NÃO repassa o SIGTERM; o Docker espera 10 s e mata com SIGKILL -> código 137)")


def section_security():
    print("\n== SEGURANÇA: quem roda o processo e o que ele pode fazer ==")
    for variant in ("naive", "good"):
        name, port = run_container(f"shop-api:{variant}", f"lab-{variant}")
        wait_ready(port)
        uid = get(port, "/")["uid"]
        write = docker("exec", name, "sh", "-c", "touch /etc/passwd.bak 2>&1 && echo escreveu || echo recusado", check=False).stdout.strip().splitlines()[-1]
        print(f"  {variant:<6} uid={uid:<6} escrever em /etc: {write}")
        cleanup(name)
    name, port = run_container("shop-api:good", "lab-hardened", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                               "--tmpfs", "/tmp", "--pids-limit", "100", "--memory", "256m")
    ready = wait_ready(port)
    print(f"  good + --read-only --cap-drop ALL --no-new-privileges --memory 256m: funciona? {get(port, '/healthz')} (pronto em {ready * 1e3:.0f} ms)")
    health = ""
    for _ in range(40):
        health = docker("inspect", name, "--format", "{{.State.Health.Status}}").stdout.strip()
        if health == "healthy":
            break
        time.sleep(1)
    print(f"  HEALTHCHECK do Dockerfile: {health}")
    cleanup(name)


def section_memory():
    print("\n== LIMITE DE MEMÓRIA: o que acontece quando o processo passa dele ==")
    name, port = run_container("shop-api:good", "lab-oom", "--memory", "128m", "--memory-swap", "128m")
    wait_ready(port)
    print("  limite de 128 MB; pedindo 40 MB de cada vez ao serviço:")
    for step in range(1, 6):
        try:
            held = get(port, "/alloc?mb=40")["held_mb"]
            print(f"    pedido {step}: segurando {held} MB")
        except Exception as error:
            print(f"    pedido {step}: sem resposta ({type(error).__name__})")
            break
    time.sleep(1)
    state = json.loads(docker("inspect", name, "--format", "{{json .State}}").stdout)
    print(f"  estado: OOMKilled={state['OOMKilled']} | código de saída {state['ExitCode']} (137 = 128 + SIGKILL) | o kernel matou o processo sem aviso")
    cleanup(name)


def section_secrets():
    print("\n== SEGREDOS: o que fica gravado na imagem para sempre ==")
    work = Path(tempfile.mkdtemp(prefix="docker-secret-"))
    (work / "Dockerfile").write_text(
        "FROM python:3.15-alpine\nARG API_TOKEN\nENV API_TOKEN=$API_TOKEN\nRUN echo \"configurado com $API_TOKEN\" > /tmp/boot.txt\n", encoding="utf-8")
    docker("build", "-q", "-t", "shop-leaky", "--build-arg", "API_TOKEN=s3cr3t-token-123", str(work))
    history = docker("history", "--no-trunc", "shop-leaky", "--format", "{{.CreatedBy}}").stdout
    env = docker("inspect", "shop-leaky", "--format", "{{.Config.Env}}").stdout
    print("  docker history mostra o token?", "s3cr3t-token-123" in history, "| docker inspect (Env) mostra?", "s3cr3t-token-123" in env)
    (work / "Dockerfile").write_text(
        "# syntax=docker/dockerfile:1\nFROM python:3.15-alpine\nRUN --mount=type=secret,id=api_token sh -c 'wc -c < /run/secrets/api_token > /tmp/size.txt'\n", encoding="utf-8")
    (work / "token.txt").write_text("s3cr3t-token-123", encoding="utf-8")
    docker("build", "-q", "-t", "shop-safe", "--secret", f"id=api_token,src={work / 'token.txt'}", str(work))
    history = docker("history", "--no-trunc", "shop-safe", "--format", "{{.CreatedBy}}").stdout
    ran = docker("run", "--rm", "shop-safe", "cat", "/tmp/size.txt").stdout.strip()
    print(f"  com --mount=type=secret: o RUN leu o segredo ({ran} bytes), mas o token aparece no history? {'s3cr3t-token-123' in history}")
    docker("rmi", "-f", "shop-leaky", "shop-safe", check=False)
    shutil.rmtree(work, ignore_errors=True)


def section_compose():
    print("\n== COMPOSE: serviço + Redis, com saúde e ordem de partida ==")
    compose = Path(__file__).parent / "compose.yaml"
    project = ["compose", "-f", str(compose), "-p", "cap69"]
    docker(*project, "down", "-v", check=False)
    _, seconds = timed(lambda: docker(*project, "up", "-d", "--build", "--wait", timeout=1800))
    ps = json.loads("[" + ",".join(docker(*project, "ps", "--format", "json").stdout.strip().splitlines()) + "]")
    print(f"  subiu em {seconds:.1f} s | " + " | ".join(f"{s['Service']}: {s['State']} ({s.get('Health') or 'sem healthcheck'})" for s in ps))
    port = int(docker(*project, "port", "api", "8000").stdout.strip().split(":")[-1])
    counts = [get(port, "/count")["count"] for _ in range(3)]
    print("  /count (o Redis guarda o contador):", counts)
    docker(*project, "restart", "api")
    wait_ready(int(docker(*project, "port", "api", "8000").stdout.strip().split(":")[-1]))
    port = int(docker(*project, "port", "api", "8000").stdout.strip().split(":")[-1])
    print("  depois de reiniciar SÓ o serviço, o contador continua (o estado mora no Redis):", get(port, "/count")["count"])
    docker(*project, "down", "-v")


SECTIONS = {"sizes": section_sizes, "cache": section_cache, "signals": section_signals, "security": section_security,
            "memory": section_memory, "secrets": section_secrets, "compose": section_compose}

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(SECTIONS)
    for name in chosen:
        SECTIONS[name]()
