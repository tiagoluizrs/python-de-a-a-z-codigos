"""Uma tabela de decisão executável: do perfil da carga ao modelo recomendado."""


def recommend(cpu_bound, items, io_wait_ratio=0.0, async_library=False, shared_state=False, latency_sensitive=False):
    """Regras do capítulo, em código."""
    if items <= 1:
        return "nenhum: não há o que paralelizar"
    if cpu_bound:
        if shared_state:
            return "threads em build sem GIL (3.15t) ou memória compartilhada entre processos"
        return "ProcessPoolExecutor (processos): contorna o GIL"
    if async_library and items > 500:
        return "asyncio: milhares de esperas com custo mínimo"
    if items > 5000:
        return "asyncio (se houver biblioteca assíncrona) ou threads com limite e fila"
    return "ThreadPoolExecutor: simples e suficiente"


SCENARIOS = [
    ("baixar 20 páginas", dict(cpu_bound=False, items=20)),
    ("baixar 20 mil páginas com httpx assíncrono", dict(cpu_bound=False, items=20000, async_library=True)),
    ("redimensionar 500 imagens", dict(cpu_bound=True, items=500)),
    ("simulação com matriz compartilhada", dict(cpu_bound=True, items=64, shared_state=True)),
    ("servidor de chat com 10 mil conexões", dict(cpu_bound=False, items=10000, async_library=True, latency_sensitive=True)),
    ("uma única consulta", dict(cpu_bound=False, items=1)),
]

if __name__ == "__main__":
    for label, profile in SCENARIOS:
        print(f"{label:<44} -> {recommend(**profile)}")
