"""SOLID aplicado sem juízo: o mesmo problema simples, resolvido com UMA função e com "toda a cerimônia"."""
import time

SIMPLE = '''
def total_with_tax(prices, rate=0.1):
    return round(sum(prices) * (1 + rate), 2)
'''

CEREMONY = '''
from abc import ABC, abstractmethod


class IPriceProvider(ABC):
    @abstractmethod
    def get_prices(self): ...


class ListPriceProvider(IPriceProvider):
    def __init__(self, prices):
        self._prices = prices

    def get_prices(self):
        return self._prices


class ITaxStrategy(ABC):
    @abstractmethod
    def apply(self, amount): ...


class PercentageTaxStrategy(ITaxStrategy):
    def __init__(self, rate):
        self._rate = rate

    def apply(self, amount):
        return amount * (1 + self._rate)


class ISumCalculator(ABC):
    @abstractmethod
    def calculate(self, values): ...


class DefaultSumCalculator(ISumCalculator):
    def calculate(self, values):
        return sum(values)


class IRoundingPolicy(ABC):
    @abstractmethod
    def round(self, value): ...


class TwoDecimalsRoundingPolicy(IRoundingPolicy):
    def round(self, value):
        return round(value, 2)


class TotalCalculatorFactory:
    @staticmethod
    def create(prices, rate):
        return TotalCalculator(ListPriceProvider(prices), PercentageTaxStrategy(rate), DefaultSumCalculator(), TwoDecimalsRoundingPolicy())


class TotalCalculator:
    def __init__(self, provider, tax, summer, rounding):
        self._provider, self._tax, self._summer, self._rounding = provider, tax, summer, rounding

    def calculate(self):
        return self._rounding.round(self._tax.apply(self._summer.calculate(self._provider.get_prices())))


def total_with_tax(prices, rate=0.1):
    return TotalCalculatorFactory.create(prices, rate).calculate()
'''


def load(source):
    ns: dict = {}
    exec(source, ns)
    return ns["total_with_tax"]


simple, ceremony = load(SIMPLE), load(CEREMONY)
prices = [19.9, 5.5, 120.0]
assert simple(prices) == ceremony(prices)
lines = lambda s: len([l for l in s.strip().splitlines() if l.strip()])
classes = lambda s: s.count("\nclass ")
print(f"mesmo resultado: {simple(prices)}")
print(f"  UMA função : {lines(SIMPLE):>3} linhas, {classes(SIMPLE)} classes")
print(f"  cerimônia  : {lines(CEREMONY):>3} linhas, {classes(CEREMONY)} classes ({lines(CEREMONY) / lines(SIMPLE):.0f}x as linhas)")

N = 200_000
for label, fn in [("UMA função", simple), ("cerimônia", ceremony)]:
    start = time.perf_counter()
    for _ in range(N):
        fn(prices)
    print(f"  {label:<11} {(time.perf_counter() - start) / N * 1e9:7.0f} ns por chamada")

print("\nquantos arquivos e níveis de chamada para achar onde o imposto é aplicado?")
print("  UMA função: 1 linha | cerimônia: total_with_tax -> Factory -> TotalCalculator -> ITaxStrategy -> PercentageTaxStrategy.apply (5 saltos)")
print("\nquando as abstrações se pagam: quando há DUAS implementações reais (o imposto varia por país), ou quando o teste precisa de um dublê;")
print("até lá, elas são código a mais para ler, e a função simples continua sendo possível de refatorar no dia em que a segunda variante chegar")
