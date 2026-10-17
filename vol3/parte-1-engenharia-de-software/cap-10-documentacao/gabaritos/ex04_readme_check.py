"""Gabarito do exercício 4."""
import re


def anchor(heading):
    text = heading.strip().lower().replace(" ", "-")
    return "".join(ch for ch in text if ch.isalnum() or ch in "-_")


def _headings(markdown):
    in_code = False
    for line in markdown.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if match:
                yield len(match.group(1)), match.group(2)


def table_of_contents(markdown, max_level=3):
    seen, lines = {}, []
    for level, title in _headings(markdown):
        base = anchor(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        if level < 2 or level > max_level:
            continue
        lines.append("  " * (level - 2) + f"- [{title}](#{base if count == 0 else f'{base}-{count}'})")
    return "\n".join(lines)


def check_readme(markdown):
    problems = set()
    non_empty = [l for l in markdown.splitlines() if l.strip()]
    if not non_empty or not re.match(r"^#\s+\S", non_empty[0]):
        problems.add("no-title")
    titles = [t.lower() for _, t in _headings(markdown)]
    for code, words in (("no-install", ("instal", "install")), ("no-usage", ("uso", "usage", "exemplo")), ("no-license", ("licen",))):
        if not any(w in t for t in titles for w in words):
            problems.add(code)
    if "```" not in markdown:
        problems.add("no-code")
    if re.search(r"\[[^\]]*\]\(\s*\)", markdown):
        problems.add("empty-link")
    if len(non_empty) < 5:
        problems.add("too-short")
    return sorted(problems)
