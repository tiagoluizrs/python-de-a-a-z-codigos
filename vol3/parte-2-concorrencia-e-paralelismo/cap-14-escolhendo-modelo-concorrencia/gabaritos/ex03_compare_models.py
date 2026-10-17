"""Gabarito do exercício 3."""
import concurrent.futures as cf
import time

KNOWN = ("sequential", "threads", "processes")


def compare_models(func, items, workers=4, models=("sequential", "threads", "processes")):
    for model in models:
        if model not in KNOWN:
            raise ValueError(f"modelo desconhecido: {model!r}")
    items = list(items)
    report = {}
    for model in models:
        start = time.perf_counter()
        if model == "sequential":
            results = [func(item) for item in items]
        else:
            pool_class = cf.ThreadPoolExecutor if model == "threads" else cf.ProcessPoolExecutor
            with pool_class(max_workers=workers) as pool:
                results = list(pool.map(func, items))
        report[model] = {"seconds": time.perf_counter() - start, "results": results}
    return report


def speedups(report, baseline="sequential"):
    base = report[baseline]["seconds"]
    return {model: base / data["seconds"] for model, data in report.items() if model != baseline}


def results_agree(report):
    outputs = [data["results"] for data in report.values()]
    return all(o == outputs[0] for o in outputs)
