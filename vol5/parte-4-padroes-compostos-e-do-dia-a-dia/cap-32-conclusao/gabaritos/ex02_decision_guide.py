"""Gabarito do exercício 2."""

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

VARIANT_PATTERNS = {"Strategy", "State", "Factory Method", "Abstract Factory", "Visitor", "Registry"}
KNOWN_FACTS = {fact for fact, _, _ in RULES} | {"variants"}
LATER = "adiar: espere a segunda variante (regra de três)"
NONE = "nenhum padrão: comece com uma função"


def recommend(**facts):
    unknown = sorted(set(facts) - KNOWN_FACTS)
    if unknown:
        raise TypeError(f"fato desconhecido: {unknown[0]}")
    variants = facts.get("variants")
    if variants is not None and (not isinstance(variants, int) or isinstance(variants, bool) or variants < 0):
        raise TypeError("variants precisa ser int")
    active = {name for name, value in facts.items() if name != "variants" and value}
    picked = [(pattern, form) for fact, pattern, form in RULES if fact in active]
    postponed = False
    if variants is not None and variants < 2:
        kept = [(p, f) for p, f in picked if p not in VARIANT_PATTERNS]
        postponed = len(kept) != len(picked)
        picked = kept
    if "one_instance" in active and "need_fakes" in active:
        picked = [(p, f) for p, f in picked if p != "Singleton"]
    result = [f"{pattern}: {form}" for pattern, form in picked]
    if postponed:
        result.append(LATER)
    return result or [NONE]
