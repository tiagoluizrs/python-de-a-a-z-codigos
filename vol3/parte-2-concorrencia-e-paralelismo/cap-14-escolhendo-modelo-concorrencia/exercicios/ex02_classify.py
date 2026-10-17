"""Exercício 2: classificar uma carga como CPU, E/S ou mista."""
import time


def cpu_ratio(func, *args, clock=time.perf_counter, cpu_clock=time.process_time, **kwargs):
    """Executa ``func(*args, **kwargs)`` e devolve ``(razão, resultado)`` onde ``razão`` é
    ``tempo de CPU / tempo de parede`` (``cpu_clock`` e ``clock`` injetáveis, para
    testar). Se o tempo de parede for 0, a razão é ``0.0``."""
    raise NotImplementedError


def classify(ratio, cpu_threshold=0.8, io_threshold=0.3):
    """``"cpu"`` se ``ratio >= cpu_threshold``; ``"io"`` se ``ratio <= io_threshold``;
    senão ``"mixed"``."""
    raise NotImplementedError


def classify_function(func, *args, **kwargs):
    """Mede e classifica: devolve ``(classificação, razão)``."""
    raise NotImplementedError
