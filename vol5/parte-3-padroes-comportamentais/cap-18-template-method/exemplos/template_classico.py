"""Template Method, forma clássica (GoF): o ESQUELETO de um algoritmo na classe base; os passos variáveis ficam para as subclasses."""
import ast
import csv
import inspect
import io
import json
import textwrap
from abc import ABC, abstractmethod
from typing import final


# --- 1. o problema: dois importadores com o MESMO roteiro copiado (validar, transformar, contar, relatar) ---
def import_csv_copy(text):
    rows, errors = [], []
    for i, row in enumerate(csv.DictReader(io.StringIO(text))):
        if not row["name"]:
            errors.append((i, "nome vazio"))
            continue
        row["name"] = row["name"].strip().title()
        rows.append(row)
    return rows, errors


def import_json_copy(text):
    rows, errors = [], []
    for i, row in enumerate(json.loads(text)):
        if not row["name"]:
            errors.append((i, "nome vazio"))
            continue
        row["name"] = row["name"].strip().title()
        rows.append(row)
    return rows, errors


print("duas cópias do mesmo roteiro:", import_csv_copy("name,age\nana,3\n,5\n")[1], import_json_copy('[{"name": "x"}]')[0])


# --- 2. o Template Method: o roteiro fixo em UM método; as subclasses preenchem os passos ---
class Importer(ABC):
    @final                                                      # o ESQUELETO não deve ser sobrescrito
    def run(self, raw):
        self.before()                                           # gancho (hook): opcional, não faz nada por padrão
        rows, errors = [], []
        for i, row in enumerate(self.parse(raw)):               # passo OBRIGATÓRIO (abstrato)
            try:
                self.validate(row)                              # passo com comportamento padrão (pode ser sobrescrito)
            except ValueError as error:
                errors.append((i, str(error)))
                continue
            rows.append(self.transform(row))
        self.after(rows, errors)
        return rows, errors

    @abstractmethod
    def parse(self, raw): ...

    def validate(self, row):
        if not row["name"]:
            raise ValueError("nome vazio")

    def transform(self, row):
        row["name"] = row["name"].strip().title()
        return row

    def before(self):
        pass

    def after(self, rows, errors):
        pass


class CsvImporter(Importer):
    def parse(self, raw):
        return csv.DictReader(io.StringIO(raw))


class JsonImporter(Importer):
    def parse(self, raw):
        return json.loads(raw)


class AuditedCsv(CsvImporter):
    def __init__(self):
        self.audit = []

    def before(self):
        self.audit.append("início")

    def after(self, rows, errors):
        self.audit.append(f"fim: {len(rows)} ok, {len(errors)} erros")

    def validate(self, row):
        super().validate(row)                                   # estende o passo padrão em vez de substituí-lo
        if len(row["name"]) > 10:
            raise ValueError("nome longo demais")


print("\nCsvImporter:", CsvImporter().run("name,age\nana,3\n,5\n"))
print("JsonImporter:", JsonImporter().run('[{"name": " bia "}]'))
audited = AuditedCsv()
print("com ganchos e validação estendida:", audited.run("name,age\nana,3\nbernardinhofilho,4\n,5\n"), audited.audit)
print("a ordem dos passos é decidida pela classe BASE (princípio de Hollywood: 'não nos chame, nós chamamos você')")

# --- 3. a fragilidade: a subclasse depende da ORDEM e do contrato da base ---
class ForgetsSuper(CsvImporter):
    def transform(self, row):
        return row                                              # esqueceu de chamar a base: o nome não é mais normalizado


print("\nsubclasse que esquece o super():", ForgetsSuper().run("name,age\n bia ,3\n")[0], "(a base mudou o contrato e a subclasse não percebeu: 'classe base frágil')")


# --- 4. a cerimônia ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\ndois importadores copiados:", measure([import_csv_copy, import_json_copy]))
print("template (Importer + 2 subclasses):", measure([Importer, CsvImporter, JsonImporter]), "| e cada formato novo é uma subclasse de 2 linhas")
