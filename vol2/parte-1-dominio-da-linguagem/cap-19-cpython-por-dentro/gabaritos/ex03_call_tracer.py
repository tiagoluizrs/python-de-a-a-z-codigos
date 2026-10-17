"""Gabarito do exercício 3."""
import sys
from collections import Counter


def trace_calls(func, *args, **kwargs):
    mon = sys.monitoring
    tool = mon.PROFILER_ID
    names = []
    here = __file__

    def on_start(code, offset):
        if code.co_filename != here:
            names.append(code.co_name)

    mon.use_tool_id(tool, "trace_calls")
    try:
        mon.register_callback(tool, mon.events.PY_START, on_start)
        mon.set_events(tool, mon.events.PY_START)
        result = func(*args, **kwargs)
    finally:
        mon.set_events(tool, 0)
        mon.register_callback(tool, mon.events.PY_START, None)
        mon.free_tool_id(tool)
    return result, names


def count_calls(func, *args, **kwargs):
    return Counter(trace_calls(func, *args, **kwargs)[1])
