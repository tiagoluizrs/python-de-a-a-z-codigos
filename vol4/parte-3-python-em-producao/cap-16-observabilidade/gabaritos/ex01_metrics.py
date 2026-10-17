"""Gabarito do exercício 1."""
import bisect
import math
import threading


def _key(label_names, labels):
    if set(labels) != set(label_names):
        raise ValueError(f"rótulos esperados {sorted(label_names)}, recebidos {sorted(labels)}")
    return tuple(labels[n] for n in label_names)


def _fmt(label_names, key, extra=""):
    parts = [f'{n}="{v}"' for n, v in zip(label_names, key)]
    if extra:
        parts.append(extra)
    return "{" + ",".join(parts) + "}" if parts else ""


class Counter:
    def __init__(self, name, label_names=()):
        self.name, self.label_names = name, tuple(label_names)
        self._values: dict = {}
        self._lock = threading.Lock()

    def inc(self, amount=1, **labels):
        if amount < 0:
            raise ValueError("um contador só sobe")
        key = _key(self.label_names, labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + amount

    def value(self, **labels):
        return float(self._values.get(_key(self.label_names, labels), 0.0))


class Histogram:
    def __init__(self, name, buckets, label_names=()):
        if not buckets or list(buckets) != sorted(set(buckets)):
            raise ValueError("buckets precisam ser não vazios e estritamente crescentes")
        self.name, self.buckets, self.label_names = name, list(buckets), tuple(label_names)
        self._series: dict = {}
        self._lock = threading.Lock()

    def observe(self, value, **labels):
        key = _key(self.label_names, labels)
        with self._lock:
            series = self._series.setdefault(key, {"counts": [0] * (len(self.buckets) + 1), "sum": 0.0})
            series["counts"][bisect.bisect_left(self.buckets, value)] += 1
            series["sum"] += value

    def counts(self, **labels):
        series = self._series.get(_key(self.label_names, labels))
        if series is None:
            return [0] * (len(self.buckets) + 1)
        total, out = 0, []
        for n in series["counts"]:
            total += n
            out.append(total)
        return out

    def quantile(self, q, **labels):
        cumulative = self.counts(**labels)
        total = cumulative[-1]
        if total == 0:
            return math.nan
        rank = q * total
        bounds = self.buckets + [math.inf]
        prev_bound, prev_count = 0.0, 0
        for bound, count in zip(bounds, cumulative):
            if count >= rank:
                if bound == math.inf:
                    return self.buckets[-1]
                return prev_bound + (bound - prev_bound) * (rank - prev_count) / max(count - prev_count, 1)
            prev_bound, prev_count = bound, count
        return self.buckets[-1]


def render(metrics):
    lines = []
    for metric in metrics:
        if isinstance(metric, Counter):
            lines.append(f"# TYPE {metric.name} counter")
            for key in sorted(metric._values):
                lines.append(f"{metric.name}_total{_fmt(metric.label_names, key)} {float(metric._values[key])}")
        else:
            lines.append(f"# TYPE {metric.name} histogram")
            for key in sorted(metric._series):
                labels = dict(zip(metric.label_names, key))
                cumulative = metric.counts(**labels)
                for bound, count in zip([repr(float(b)) for b in metric.buckets] + ["+Inf"], cumulative):
                    le = 'le="' + bound + '"'
                    lines.append(f"{metric.name}_bucket{_fmt(metric.label_names, key, le)} {count}")
                lines.append(f"{metric.name}_sum{_fmt(metric.label_names, key)} {float(metric._series[key]['sum'])}")
                lines.append(f"{metric.name}_count{_fmt(metric.label_names, key)} {cumulative[-1]}")
    return "\n".join(lines) + "\n"
