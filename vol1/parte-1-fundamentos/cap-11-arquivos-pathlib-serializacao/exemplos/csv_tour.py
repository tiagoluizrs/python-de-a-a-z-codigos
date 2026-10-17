"""csv: reader/writer, DictReader/DictWriter, aspas e BOM do Excel."""
import csv
import io
import tempfile
from pathlib import Path

rows = [
    ["name", "city", "note"],
    ["Ana", "São Paulo", 'said "hi"'],
    ["Bia", "Rio, RJ", "line 1\nline 2"],
]

with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
    path = Path(tmp) / "people.csv"

    # newline="" é OBRIGATÓRIO: o módulo csv cuida das quebras de linha
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    print(path.read_text(encoding="utf-8", newline=""))

    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            print(row)

    # DictReader: o cabeçalho vira as chaves; tudo é str
    with open(path, encoding="utf-8", newline="") as f:
        for record in csv.DictReader(f):
            print(record["name"], "|", record["note"])

    # DictWriter
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["id", "price"])
    writer.writeheader()
    writer.writerow({"id": 1, "price": 9.5})
    writer.writerow({"id": 2, "price": 10})
    print(repr(out.getvalue()))      # note o \r\n no fim das linhas

# --- tudo é texto: números precisam de conversão explícita
reader = csv.DictReader(io.StringIO("id,price\n1,9.5\n2,10\n"))
print([(int(r["id"]), float(r["price"])) for r in reader])

# --- outro delimitador (planilhas em português usam ";")
text = "name;price\nAna;1,50\n"
print(list(csv.reader(io.StringIO(text), delimiter=";")))

# --- linhas com número de campos diferente
reader = csv.DictReader(io.StringIO("a,b\n1,2,3\n4\n"))
print(list(reader))                  # restkey=None, restval=None

# --- BOM: o Excel abre melhor CSV com utf-8-sig
raw = "name\nAna\n".encode("utf-8-sig")
print(raw[:3], raw[3:])
print(next(csv.reader(io.StringIO(raw.decode("utf-8")))))   # BOM vaza
print(next(csv.reader(io.StringIO(raw.decode("utf-8-sig")))))

# --- Sniffer: adivinha o dialeto (use com cautela)
print(csv.Sniffer().sniff("a;b;c\n1;2;3\n").delimiter)
