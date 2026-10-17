"""Gabarito do exercício 3."""
from urllib import robotparser


class Robots:
    def __init__(self, text, user_agent, default_delay=1.0):
        self.user_agent = user_agent
        self.default_delay = default_delay
        self.parser = robotparser.RobotFileParser()
        self.parser.parse(text.splitlines())

    def allowed(self, url):
        return self.parser.can_fetch(self.user_agent, url)

    def delay(self):
        declared = self.parser.crawl_delay(self.user_agent)
        return max(float(declared), self.default_delay) if declared is not None else self.default_delay

    def filter_urls(self, urls):
        ok, blocked = [], []
        for url in urls:
            (ok if self.allowed(url) else blocked).append(url)
        return ok, blocked
