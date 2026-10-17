"""Corpos grandes: stream sem carregar tudo na memória; upload; retomada."""
import io
import os
import tempfile
import tracemalloc

import httpx

from demo_server import serve

with serve() as base:
    # 1. read() carrega tudo; stream() entrega em pedaços
    for label, streaming in (("response.content (tudo de uma vez)", False), ("client.stream() + iter_bytes(64 KB)", True)):
        tracemalloc.start()
        total = 0
        with httpx.Client() as client:
            if streaming:
                with client.stream("GET", f"{base}/big", params={"kb": 20_000}) as response:
                    for chunk in response.iter_bytes(65_536):
                        total += len(chunk)
            else:
                total = len(client.get(f"{base}/big", params={"kb": 20_000}).content)
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        print(f"  baixar {total / 1e6:.1f} MB com {label:<38} pico de memória: {peak / 1e6:6.1f} MB")

    # 2. linhas de uma resposta em fluxo contínuo (como um log ao vivo)
    with httpx.stream("GET", f"{base}/stream", params={"n": 4}) as response:
        print("\niter_lines():", [line for line in response.iter_lines()])

    # 3. baixar para um arquivo com progresso
    path = os.path.join(tempfile.mkdtemp(), "arquivo.bin")
    done = 0
    with httpx.stream("GET", f"{base}/big", params={"kb": 4096}) as response, open(path, "wb") as handle:
        total = int(response.headers["content-length"])
        for chunk in response.iter_bytes(512 * 1024):
            handle.write(chunk)
            done += len(chunk)
    print(f"\nbaixado em arquivo: {done / 1e6:.1f} MB de {total / 1e6:.1f} MB | arquivo no disco: {os.path.getsize(path) / 1e6:.1f} MB")

    # 4. retomar um download interrompido com o cabeçalho Range
    data = httpx.get(f"{base}/range").content
    partial = data[:40_000]
    with httpx.stream("GET", f"{base}/range", headers={"Range": f"bytes={len(partial)}-"}) as response:
        resumed = partial + b"".join(response.iter_bytes())
        print(f"retomada: status {response.status_code} (206 = conteúdo parcial) | Content-Range {response.headers['content-range']} | arquivo completo igual: {resumed == data}")

    # 5. upload: arquivo em memória e gerador (sem montar o corpo inteiro)
    upload = httpx.post(f"{base}/upload", files={"arquivo": ("dados.txt", io.BytesIO(b"conteudo " * 1000), "text/plain")})
    print("\nupload multipart:", upload.json()["received_bytes"], "bytes, tipo", upload.json()["content_type"].split(";")[0])

    def generate():
        for i in range(5):
            yield b"parte-%d;" % i

    streamed = httpx.post(f"{base}/upload", content=generate())
    print("upload por gerador (Transfer-Encoding: chunked):", streamed.json()["received_bytes"], "bytes")
