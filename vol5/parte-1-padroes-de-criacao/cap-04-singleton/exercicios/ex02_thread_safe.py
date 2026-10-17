"""Exercício 2: um decorador de classe que torna QUALQUER classe um singleton, seguro com threads."""


def singleton(cls):
    """Transforma ``cls`` em um singleton e a devolve (continua sendo uma classe: ``isinstance(Pool(), Pool)`` é verdadeiro).

    * a primeira chamada cria a instância e roda o ``__init__`` UMA vez, com os argumentos dessa chamada; as seguintes devolvem a mesma instância
      e IGNORAM os argumentos (e o ``__init__`` NÃO roda de novo);
    * seguro com threads: com 8 threads chamando ao mesmo tempo, o ``__init__`` roda exatamente UMA vez (use uma ``threading.Lock`` com dupla
      verificação) e nenhuma thread recebe uma instância ainda não inicializada;
    * se o ``__init__`` levantar uma exceção, nada é guardado: a próxima chamada tenta de novo;
    * ``cls.reset_singleton()`` (``staticmethod`` ou ``classmethod`` acrescentado à classe) descarta a instância;
    * ``cls.singleton_created()`` devolve quantas instâncias foram criadas até agora (não zera no reset)."""
    raise NotImplementedError
