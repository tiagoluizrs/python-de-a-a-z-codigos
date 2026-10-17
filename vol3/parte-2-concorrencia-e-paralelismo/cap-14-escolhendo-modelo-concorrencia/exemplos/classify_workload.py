"""CPU ou E/S? O tempo de CPU contra o tempo de parede responde."""
import time

import tasks


def cpu_ratio(func, *args):
    """Fração do tempo de parede em que o processo ESTEVE usando a CPU."""
    wall, cpu = time.perf_counter(), time.process_time()
    func(*args)
    return (time.process_time() - cpu) / (time.perf_counter() - wall)


def fake_http_request():
    time.sleep(0.05)
    sum(range(20_000))


def parse_json_like():
    sum(i * i for i in range(300_000))


if __name__ == "__main__":
    for label, func in [("cpu_task", tasks.cpu_task), ("io_task(0.1)", lambda: tasks.io_task(0.1)), ("mixed_task", tasks.mixed_task),
                        ("pedido de rede simulado", fake_http_request), ("análise de dados", parse_json_like)]:
        ratio = cpu_ratio(func)
        kind = "CPU" if ratio > 0.8 else "E/S" if ratio < 0.3 else "misto"
        print(f"{label:<26} CPU/parede = {ratio:4.2f}  -> {kind}")
    print("\nregra: razão perto de 1 = a tarefa passa o tempo calculando (processos/paralelismo);")
    print("       razão perto de 0 = passa o tempo esperando (threads ou asyncio bastam)")
