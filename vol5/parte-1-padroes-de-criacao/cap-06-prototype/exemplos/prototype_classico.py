"""Prototype, forma clássica (GoF): criar objetos CLONANDO um exemplar existente, em vez de construí-los do zero."""
import copy
import json
import pickle
import time
from abc import ABC, abstractmethod


# --- 1. o problema: construir é caro (ler, interpretar e montar) e vários objetos partem do mesmo modelo ---
TEMPLATE_TEXT = json.dumps({"title": "", "sections": [{"heading": f"Seção {i}", "items": [{"text": f"item {j}", "tags": ["a", "b"]} for j in range(20)]} for i in range(25)]})


class Document:
    def __init__(self, text):
        self.data = json.loads(text)                        # "ler e interpretar o modelo": o custo de criar do zero
        self.title = self.data["title"]


def best(fn, n=300):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"construir do zero a partir do texto: {best(lambda: Document(TEMPLATE_TEXT)):7.1f} µs")


# --- 2. a forma clássica: a interface Prototype com clone() ---
class Prototype(ABC):
    @abstractmethod
    def clone(self): ...


class Shape(Prototype):
    def __init__(self, kind, color, points):
        self.kind, self.color, self.points = kind, color, points

    def clone(self):
        return Shape(self.kind, self.color, list(self.points))      # cópia "à mão": é preciso lembrar de cada campo

    def __repr__(self):
        return f"Shape({self.kind!r}, {self.color!r}, {self.points})"


square = Shape("quadrado", "azul", [(0, 0), (1, 1)])
twin = square.clone()
twin.color = "verde"
twin.points.append((2, 2))
print("\nclone() à mão:", square, "|", twin)


# --- 3. o registro de protótipos (o 'prototype manager' do GoF) ---
class PrototypeRegistry:
    def __init__(self):
        self._items = {}

    def register(self, name, prototype):
        self._items[name] = prototype

    def create(self, name):
        return self._items[name].clone()


registry = PrototypeRegistry()
registry.register("quadrado-azul", square)
registry.register("circulo-vermelho", Shape("círculo", "vermelho", [(0, 0)]))
print("registro:", registry.create("quadrado-azul"), registry.create("circulo-vermelho"))

# --- 4. o ponto fraco do clone() à mão: esquecer um campo (ou aninhar um nível) e compartilhar estado sem querer ---
class Layer:
    def __init__(self, name, shapes):
        self.name, self.shapes = name, shapes

    def clone(self):
        return Layer(self.name, self.shapes)                          # esqueceu de clonar a lista: cópia RASA


base = Layer("fundo", [Shape("quadrado", "azul", [])])
other = base.clone()
other.shapes.append(Shape("círculo", "verde", []))
print("\nclone() esqueceu de clonar a lista:", len(base.shapes), "formas no original (era 1): o clone alterou o modelo")

# --- 5. a alternativa de uma linha: o módulo copy (veja o exemplo seguinte) e a comparação de custo para dados em JSON ---
obj = json.loads(TEMPLATE_TEXT)
print("\nduplicar uma estrutura de 500 itens:")
print(f"  json.loads(texto)                 {best(lambda: json.loads(TEMPLATE_TEXT)):7.1f} µs  (reinterpretar o texto)")
print(f"  copy.deepcopy(obj)                {best(lambda: copy.deepcopy(obj)):7.1f} µs")
print(f"  pickle.loads(pickle.dumps(obj))   {best(lambda: pickle.loads(pickle.dumps(obj))):7.1f} µs")
print(f"  copy.copy(obj)  (só o 1º nível)   {best(lambda: copy.copy(obj)):7.1f} µs")
print("para dados em JSON, o deepcopy NÃO é o mais rápido: clonar só vale a pena quando construir é mais caro que copiar (rede, disco, cálculo)")
