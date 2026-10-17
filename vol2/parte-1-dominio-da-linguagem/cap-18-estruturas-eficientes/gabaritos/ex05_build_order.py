"""Gabarito do exercício 5."""
import graphlib


def build_layers(deps):
    sorter = graphlib.TopologicalSorter(deps)
    try:
        sorter.prepare()
    except graphlib.CycleError as error:
        raise ValueError("ciclo: " + " -> ".join(map(str, error.args[1]))) from None
    layers = []
    while sorter.is_active():
        ready = sorter.get_ready()
        layers.append(sorted(ready))
        sorter.done(*ready)
    return layers


def critical_path_length(deps):
    return len(build_layers(deps))
