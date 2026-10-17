"""Exercício 3: respeitar o robots.txt sem baixar nada (o texto das regras chega pronto)."""


class Robots:
    """Envolve ``urllib.robotparser.RobotFileParser`` com a política do seu raspador."""

    def __init__(self, text: str, user_agent: str, default_delay: float = 1.0):
        """``text`` é o conteúdo do robots.txt; ``user_agent`` é o seu (ex.: ``"curso-bot"``); ``default_delay`` é a
        espera mínima (segundos) entre requisições quando o site não declara um ``Crawl-delay``."""
        raise NotImplementedError

    def allowed(self, url: str) -> bool:
        """Pode ler esta URL (completa, como ``http://site/catalog?page=2``)? Sempre considere o SEU user agent."""
        raise NotImplementedError

    def delay(self) -> float:
        """Segundos de espera entre requisições: o ``Crawl-delay`` do site para o seu user agent, mas NUNCA menos que
        ``default_delay`` (se o site pedir 1 s e o seu padrão for 3 s, vale 3 s). O ``RobotFileParser`` só entende
        ``Crawl-delay`` com número INTEIRO de segundos."""
        raise NotImplementedError

    def filter_urls(self, urls: list[str]) -> tuple[list[str], list[str]]:
        """Divide ``urls`` em ``(permitidas, proibidas)`` mantendo a ordem."""
        raise NotImplementedError
