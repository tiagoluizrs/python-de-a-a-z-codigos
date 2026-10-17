"""A mesma carga, quatro modelos: o que cada um resolve (e o que não resolve)."""
import asyncio

import models
import tasks


async def async_sleep(seconds):
    await asyncio.sleep(seconds)
    return seconds


def run_cpu(label, n):
    items = [n] * 16
    print(f"CARGA DE CPU: 16 tarefas {label} (Python puro)")
    sequential, _ = models.timed(models.run_sequential, tasks.cpu_task, items)
    print(f"  sequencial                      {sequential:6.2f} s   1,0x")
    for name, runner in [("threads (16)", lambda: models.run_threads(tasks.cpu_task, items, 16)),
                         ("processos (16)", lambda: models.run_processes(tasks.cpu_task, items, 16)),
                         ("asyncio.to_thread (16)", lambda: models.run_asyncio(tasks.cpu_task, items))]:
        elapsed, _ = models.timed(runner)
        print(f"  {name:<30}{elapsed:6.2f} s   {sequential / elapsed:4.1f}x")
    print()


def run_io():
    waits = [0.1] * 50
    print("CARGA DE E/S: 50 esperas de 0,1 s")
    sequential, _ = models.timed(models.run_sequential, tasks.io_task, waits)
    print(f"  sequencial                      {sequential:6.2f} s   1,0x")
    for name, runner in [("threads (50)", lambda: models.run_threads(tasks.io_task, waits, 50)),
                         ("threads (8)", lambda: models.run_threads(tasks.io_task, waits, 8)),
                         ("processos (16)", lambda: models.run_processes(tasks.io_task, waits, 16)),
                         ("asyncio (corrotinas)", lambda: models.run_asyncio_native(async_sleep, waits))]:
        elapsed, _ = models.timed(runner)
        print(f"  {name:<30}{elapsed:6.2f} s   {sequential / elapsed:4.1f}x")


if __name__ == "__main__":
    print(f"máquina: {models.CPUS} processadores lógicos\n")
    for label, n in (("curtas (~0,1 s)", 1_500_000), ("longas (~0,5 s)", 7_000_000)):
        run_cpu(label, n)
    run_io()
