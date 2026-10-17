"""Exercício 2: o guia de decisão como código: da situação ao padrão, com as exceções que o volume ensinou (a regra de três, o Singleton que vira injeção, "nenhum padrão")."""

# (Pronto, NÃO edite.) A tabela do guia: (fato, padrão, forma pythônica). A ORDEM da tabela é a ordem das recomendações.
RULES = [
    ("varies_algorithm", "Strategy", "uma função"),
    ("state_changes_behavior", "State", "Enum + tabela de transições"),
    ("notify_many", "Observer", "uma lista de funções"),
    ("undo_needed", "Command", "o par (do, undo)"),
    ("undo_needed", "Memento", "estado imutável"),
    ("whole_part", "Composite", "dataclass com children e __iter__"),
    ("incompatible_interface", "Adapter", "uma função ou um Protocol"),
    ("simplify_subsystem", "Facade", "uma função ou um módulo"),
    ("wrap_behavior", "Decorator", "@decorador com functools.wraps"),
    ("control_access", "Proxy", "__getattr__ ou property"),
    ("many_similar_objects", "Flyweight", "__slots__ e functools.cache"),
    ("one_instance", "Singleton", "o módulo"),
    ("create_by_name", "Factory Method", "um dicionário de classes"),
    ("product_families", "Abstract Factory", "um dataclass de funções"),
    ("step_by_step", "Builder", "argumentos nomeados e dataclass"),
    ("clone_existing", "Prototype", "copy.copy ou replace"),
    ("expensive_resource", "Object Pool", "queue.Queue e contextmanager"),
    ("handler_pipeline", "Chain of Responsibility", "uma lista de funções ou middleware"),
    ("many_to_many", "Mediator", "um objeto simples"),
    ("type_operations", "Visitor", "singledispatch ou match"),
    ("rules_as_data", "Interpreter", "ast com lista branca"),
    ("traverse", "Iterator", "um gerador"),
    ("absence_is_normal", "Null Object", "coleção vazia ou valor padrão"),
    ("hide_storage", "Repository", "uma coleção"),
    ("hide_storage", "Unit of Work", "@contextmanager"),
    ("combine_rules", "Specification", "predicados com & | ~"),
    ("extensible_by_others", "Registry", "decorador e entry points"),
    ("need_fakes", "Injeção de Dependência", "parâmetros e raiz de composição"),
]

VARIANT_PATTERNS = {"Strategy", "State", "Factory Method", "Abstract Factory", "Visitor", "Registry"}   # os que só se pagam com 2 ou mais variantes
KNOWN_FACTS = {fact for fact, _, _ in RULES} | {"variants"}
LATER = "adiar: espere a segunda variante (regra de três)"
NONE = "nenhum padrão: comece com uma função"


def recommend(**facts) -> list[str]:
    """Recomenda padrões a partir de fatos sobre o problema, como uma lista de textos ``"Padrão: forma pythônica"``.

    * um fato com NOME desconhecido (fora de ``KNOWN_FACTS``): ``TypeError(f"fato desconhecido: {nome}")`` (o primeiro, em ordem alfabética, se há vários);
    * ``variants`` (opcional) é o número de variantes que o problema TEM (``int >= 0``, ``bool`` NÃO vale; senão ``TypeError("variants precisa ser int")``); os demais fatos são verdadeiros
      se o valor é verdadeiro (``False``, ``0`` e ``None`` os desligam);
    * a lista segue a ORDEM de ``RULES`` (um fato verdadeiro traz todas as suas linhas: ``undo_needed`` traz Command e Memento; ``hide_storage``, Repository e Unit of Work);
    * REGRA DE TRÊS: se ``variants`` foi dado e é MENOR que 2, os padrões de ``VARIANT_PATTERNS`` saem da lista e, se algum saiu, ``LATER`` é acrescentado NO FIM;
    * SINGLETON QUE VIRA INJEÇÃO: se ``one_instance`` e ``need_fakes`` são ambos verdadeiros, o ``Singleton`` sai (a injeção de dependência já cobre os dois);
    * se, no fim, a lista está vazia (nenhum fato verdadeiro, ou tudo adiado e sem nada mais), o resultado é ``[NONE]``... mas se só ``LATER`` restou, devolva ``[LATER]``
      (o aviso de que algo foi adiado vale mais que o ``NONE``)."""
    raise NotImplementedError
