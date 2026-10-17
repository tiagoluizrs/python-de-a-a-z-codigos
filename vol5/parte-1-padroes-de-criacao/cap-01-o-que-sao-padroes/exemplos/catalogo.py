"""O catálogo do livro: os 23 padrões do GoF (Gamma, Helm, Johnson, Vlissides, 1994) mais os extras do dia a dia, com o que o Python faz por eles."""
from collections import Counter

# verdict: "embutido" (a linguagem já tem o mecanismo), "simplificado" (poucas linhas com recursos nativos) ou "igual" (a estrutura clássica continua valendo)
CATALOG = [
    # criação
    {"name": "Factory Method", "family": "criação", "chapter": 2, "verdict": "simplificado", "python": "classes são objetos: funções fábrica e @classmethod"},
    {"name": "Abstract Factory", "family": "criação", "chapter": 3, "verdict": "simplificado", "python": "um módulo ou um dict de callables por família"},
    {"name": "Singleton", "family": "criação", "chapter": 4, "verdict": "embutido", "python": "o módulo, importado uma única vez"},
    {"name": "Builder", "family": "criação", "chapter": 5, "verdict": "simplificado", "python": "argumentos nomeados, valores padrão e dataclasses"},
    {"name": "Prototype", "family": "criação", "chapter": 6, "verdict": "embutido", "python": "copy.copy, copy.deepcopy e dataclasses.replace"},
    # estruturais
    {"name": "Adapter", "family": "estrutural", "chapter": 8, "verdict": "igual", "python": "a duck typing reduz o trabalho, mas o objeto intermediário continua"},
    {"name": "Facade", "family": "estrutural", "chapter": 9, "verdict": "igual", "python": "um módulo ou uma função que esconde um subsistema"},
    {"name": "Decorator", "family": "estrutural", "chapter": 10, "verdict": "embutido", "python": "a sintaxe @ e functools.wraps"},
    {"name": "Composite", "family": "estrutural", "chapter": 11, "verdict": "igual", "python": "a árvore continua; __iter__ e recursão ajudam"},
    {"name": "Proxy", "family": "estrutural", "chapter": 12, "verdict": "simplificado", "python": "__getattr__, property e descritores"},
    {"name": "Bridge", "family": "estrutural", "chapter": 13, "verdict": "simplificado", "python": "composição + duck typing, sem hierarquias paralelas"},
    {"name": "Flyweight", "family": "estrutural", "chapter": 14, "verdict": "simplificado", "python": "interning, __slots__ e functools.cache"},
    # comportamentais
    {"name": "Strategy", "family": "comportamental", "chapter": 15, "verdict": "embutido", "python": "funções são valores"},
    {"name": "Observer", "family": "comportamental", "chapter": 16, "verdict": "simplificado", "python": "uma lista de callables"},
    {"name": "Command", "family": "comportamental", "chapter": 17, "verdict": "embutido", "python": "callables e functools.partial"},
    {"name": "Template Method", "family": "comportamental", "chapter": 18, "verdict": "simplificado", "python": "ganchos opcionais, funções de ordem superior e gerenciadores de contexto"},
    {"name": "Iterator", "family": "comportamental", "chapter": 19, "verdict": "embutido", "python": "o protocolo de iteração e os geradores"},
    {"name": "State", "family": "comportamental", "chapter": 20, "verdict": "simplificado", "python": "enum, dict de funções e match"},
    {"name": "Chain of Responsibility", "family": "comportamental", "chapter": 21, "verdict": "simplificado", "python": "uma lista de funções percorrida em ordem"},
    {"name": "Mediator", "family": "comportamental", "chapter": 22, "verdict": "igual", "python": "o objeto central continua necessário"},
    {"name": "Memento", "family": "comportamental", "chapter": 23, "verdict": "simplificado", "python": "copy, pickle e dataclasses.replace"},
    {"name": "Visitor", "family": "comportamental", "chapter": 24, "verdict": "simplificado", "python": "functools.singledispatch e match"},
    {"name": "Interpreter", "family": "comportamental", "chapter": 25, "verdict": "igual", "python": "o módulo ast e o match sobre árvores"},
]

# padrões fora do GoF que o dia a dia de quem programa em Python encontra o tempo todo
EXTRAS = [
    {"name": "Object Pool", "chapter": 7}, {"name": "MVC e padrões compostos", "chapter": 26}, {"name": "Null Object", "chapter": 27},
    {"name": "Repository e Unit of Work", "chapter": 28}, {"name": "Specification", "chapter": 29}, {"name": "Registry e plugins", "chapter": 30},
    {"name": "Injeção de Dependência", "chapter": 31},
]

print("GoF por família:", dict(Counter(p["family"] for p in CATALOG)), "| total:", len(CATALOG))
by_verdict = Counter(p["verdict"] for p in CATALOG)
print("o que o Python faz por eles:", dict(by_verdict))
print(f"  embutidos ou simplificados: {by_verdict['embutido'] + by_verdict['simplificado']} de {len(CATALOG)}")
print("\nembutidos na linguagem (você os usa sem notar):")
for p in CATALOG:
    if p["verdict"] == "embutido":
        print(f"  {p['name']:<10} -> {p['python']}")
print("\nos que continuam com a estrutura clássica:", ", ".join(p["name"] for p in CATALOG if p["verdict"] == "igual"))
print("\nextras do livro:", ", ".join(f"{e['name']} (cap. {e['chapter']})" for e in EXTRAS))
chapters = sorted([p["chapter"] for p in CATALOG] + [e["chapter"] for e in EXTRAS])
print("capítulos cobertos pelo catálogo:", chapters[0], "a", chapters[-1], "| sem buracos:", chapters == list(range(2, 32)))
