"""JSON Lines: um objeto JSON por linha, ideal para streaming."""
import json
import tempfile
from pathlib import Path

events = [{"id": i, "msg": f"evento {i}"} for i in range(3)]

with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
    path = Path(tmp) / "events.jsonl"

    # anexar é barato: não é preciso reler nem reescrever o arquivo
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(path.read_text(encoding="utf-8"), end="")

    # ler: uma linha por vez, memória constante
    with open(path, encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            print(event["id"], event["msg"])

    # um JSON único com lista exigiria ler tudo antes de usar
    big = json.dumps(events)
    print(len(big), "bytes em um único documento")
