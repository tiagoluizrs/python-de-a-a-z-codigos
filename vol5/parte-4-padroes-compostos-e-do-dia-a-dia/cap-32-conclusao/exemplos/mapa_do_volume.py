"""O mapa do volume: todos os padrões estudados, o que o Python faz por cada um e o número que ficou (os dados deste arquivo alimentam as tabelas do capítulo)."""
from collections import Counter

# (capítulo, padrão, família, o que o Python faz [só os 23 do GoF], a forma pythônica, o número que ficou)
PATTERNS = [
    (2, "Factory Method", "criação", "simplificado", "dicionário de classes, classe como argumento, @classmethod", "23 linhas e 6 classes contra 14 e 2; ~72 a ~113 ns"),
    (3, "Abstract Factory", "criação", "simplificado", "dataclass de funções, módulo ou dict", "52 linhas e 12 classes contra 21 e 1; mesmo tempo (~4,4 µs)"),
    (4, "Singleton", "criação", "embutido", "o módulo, ou functools.cache", "~105 ns (__new__) contra ~35-40 ns; 8 threads criaram 8 sem trava"),
    (5, "Builder", "criação", "simplificado", "argumentos nomeados + dataclass(kw_only)", "30 linhas contra 9; ~650 ns em ambos os casos"),
    (6, "Prototype", "criação", "embutido", "copy.copy, deepcopy e replace", "deepcopy ~870 µs contra json.loads ~230 µs (500 itens)"),
    (7, "Object Pool", "criação", "fora do GoF", "queue.Queue + contextmanager", "conexão ~260 µs para ~35 µs; objeto barato ~120 ns para ~1.080 ns (9× pior)"),
    (8, "Adapter", "estrutural", "igual", "duck typing, Protocol, função ou __getattr__", "delegação por __getattr__ ~4× a chamada direta"),
    (9, "Facade", "estrutural", "igual", "uma função ou o __init__.py com __all__", "cliente de 6 nomes para 1; código novo: 17 linhas"),
    (10, "Decorator", "estrutural", "embutido", "@decorador com functools.wraps", "~30 ns por camada de objeto; ~75 ns por decorador de função"),
    (11, "Composite", "estrutural", "igual", "dataclass com children + __iter__ com yield from", "29 linhas e 3 classes; yield from fundo ~11× mais lento que pilha explícita"),
    (12, "Proxy", "estrutural", "simplificado", "__getattr__, property e descritores", "__getattr__ ~158 ns (4× o atributo normal, ~36 ns)"),
    (13, "Bridge", "estrutural", "simplificado", "Protocol ou função", "~100 ns direto contra ~320 ns pela ponte"),
    (14, "Flyweight", "estrutural", "simplificado", "__slots__, functools.cache e sys.intern", "117,7 MB para 7,7 MB; sys.intern 2,79 MB para 0,44 MB"),
    (15, "Strategy", "comportamental", "embutido", "uma função", "21 linhas e 5 classes contra 8 e 0; ~117 a ~150 ns"),
    (16, "Observer", "comportamental", "simplificado", "uma lista de funções (Signal)", "~60 ns por observador; interfaces: 13 linhas e 2 classes"),
    (17, "Command", "comportamental", "embutido", "callable, partial ou o par (do, undo)", "46 linhas e 5 classes contra 39 e 1 (-15%)"),
    (18, "Template Method", "comportamental", "simplificado", "função que recebe os passos; @contextmanager", "32 linhas e 3 classes contra 23 e 0"),
    (19, "Iterator", "comportamental", "embutido", "o protocolo de iteração e o gerador", "16 linhas e 1 classe contra 5; lista 40 MB contra gerador 0,4 KB"),
    (20, "State", "comportamental", "simplificado", "Enum + tabela de transições", "43 linhas e 7 classes contra 13 + 5 de dados; ~474 ns contra ~770 ns"),
    (21, "Chain of Responsibility", "comportamental", "simplificado", "lista de funções, middleware, ChainMap", "24 linhas e 2 classes contra 11 e 0; ~50 ns por camada"),
    (22, "Mediator", "comportamental", "igual", "objeto simples, regras como dados, queue.Queue", "10 usuários: 90 ligações contra 10; ~210 ns por notificação"),
    (23, "Memento", "comportamental", "simplificado", "estado imutável (dataclass frozen)", "27,6 MB para 4,1 MB (7×); comando inverso 549× menos memória"),
    (24, "Visitor", "comportamental", "simplificado", "singledispatch, match e ast.NodeVisitor", "1.023 nós: clássico 58 µs, match 209 µs, singledispatch 330 µs"),
    (25, "Interpreter", "comportamental", "igual", "ast + lista branca + closures (nunca eval)", "analisar ~12,8 µs contra interpretar ~0,8 µs; closure ~6× o ast"),
    (26, "Padrões compostos: MVC", "composto", "fora do GoF", "estilo Elm: estado imutável, update e view puros", "69 linhas e 4 classes contra 12; histórico 16,1 MB para 1,9 MB (9×)"),
    (27, "Null Object", "do dia a dia", "fora do GoF", "coleção vazia, valor padrão, noop", "guarda ~35 ns contra NullLogger ~77 ns; camaleão ~3,3× mais lento"),
    (28, "Repository e Unit of Work", "do dia a dia", "fora do GoF", "coleção + @contextmanager", "um commit por linha 237× mais lento; get ~31 µs contra ~0,07 µs"),
    (29, "Specification", "do dia a dia", "fora do GoF", "predicados com &, | e ~", "82 linhas e 8 classes contra 2; Python e SQL só concordam com a lógica de 3 valores"),
    (30, "Registry e Plugins", "do dia a dia", "fora do GoF", "decorador, __init_subclass__ e entry points", "dict ~72 ns contra if/elif ~637 ns; carga preguiçosa 60 ms para 3 ms (19×)"),
    (31, "Injeção de Dependência", "do dia a dia", "fora do GoF", "parâmetro, partial e contêiner", "à mão 0,36 µs, contêiner 4 µs (170 µs sem cache da assinatura)"),
]

# pares "antes e depois" medidos nos próprios capítulos: (padrão, linhas e classes do desenho clássico, a forma pythônica)
CEREMONY = [
    ("Strategy", (21, 5), (8, 0)),
    ("Abstract Factory", (52, 12), (21, 1)),
    ("Builder", (30, None), (9, None)),
    ("Command", (46, 5), (39, 1)),
    ("Template Method", (32, 3), (23, 0)),
    ("Iterator", (16, 1), (5, 0)),
    ("State", (43, 7), (18, 0)),
    ("Chain of Responsibility", (24, 2), (11, 0)),
]


def by_family():
    return Counter(family for _, _, family, *_ in PATTERNS)


def gof_verdicts():
    return Counter(verdict for _, _, _, verdict, *_ in PATTERNS if verdict != "fora do GoF")


def check_coverage():
    chapters = [chapter for chapter, *_ in PATTERNS]
    assert chapters == list(range(2, 32)), "os capítulos de padrões vão de 2 a 31, sem repetição"
    return len(chapters)


def savings(classic, pythonic):
    return round((1 - pythonic[0] / classic[0]) * 100)


if __name__ == "__main__":
    n = check_coverage()
    print(f"{n} capítulos de padrões (2 a 31) + a introdução (1) e esta conclusão (32) = {n + 2} capítulos")
    print("por família:", dict(by_family()))
    gof = gof_verdicts()
    print("os 23 do GoF e o que o Python faz por eles:", dict(gof), "| total", sum(gof.values()), "| com mecanismo nativo:", gof["embutido"] + gof["simplificado"], "de", sum(gof.values()))
    print("\ncerimônia, do desenho clássico para a forma pythônica (linhas):")
    for name, classic, pythonic in CEREMONY:
        classes = f" (classes: {classic[1]} -> {pythonic[1]})" if classic[1] is not None else ""
        print(f"  {name:24} {classic[0]:3} -> {pythonic[0]:3} linhas, -{savings(classic, pythonic):2}%{classes}")
    gains = {name: savings(c, p) for name, c, p in CEREMONY}
    smallest, largest = min(gains, key=gains.get), max(gains, key=gains.get)
    print(f"  média: -{sum(gains.values()) / len(gains):.0f}% de linhas; a economia varia de -{gains[smallest]}% ({smallest}, que carrega estado) a -{gains[largest]}% ({largest}): onde há estado e regras, o padrão encolhe pouco")
    print("\no número que ficou, por capítulo:")
    for chapter, name, family, verdict, form, number in PATTERNS:
        print(f"  {chapter:2} {name:28} {number}")
