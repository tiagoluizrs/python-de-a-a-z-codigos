"""Gabarito do exercício 5."""
import tomllib


def _release(text):
    return tuple(int(part) for part in text.split("."))


def locked_versions(lock_text):
    data = tomllib.loads(lock_text)
    return {package["name"]: package["version"] for package in data.get("package", [])}


def diff_locks(old_text, new_text):
    old, new = locked_versions(old_text), locked_versions(new_text)
    result = {"added": {}, "removed": {}, "upgraded": {}, "downgraded": {}}
    for name in sorted(set(old) | set(new)):
        if name not in old:
            result["added"][name] = new[name]
        elif name not in new:
            result["removed"][name] = old[name]
        elif old[name] != new[name]:
            kind = "upgraded" if _release(new[name]) > _release(old[name]) else "downgraded"
            result[kind][name] = (old[name], new[name])
    return result


def summarize(diff):
    def part(key, singular):
        n = len(diff[key])
        return f"{n} {singular if n == 1 else singular + 's'}"

    return ", ".join([part("added", "adicionado"), part("removed", "removido"),
                      part("upgraded", "atualizado"), part("downgraded", "rebaixado")])
