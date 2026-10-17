"""math, decimal, fractions, statistics."""
import math
import math.integer as mint      # novo no 3.15 (PEP 791)
import statistics
from decimal import Decimal
from fractions import Fraction

print(math.isqrt(99), math.comb(5, 2), math.perm(5, 2))
print(math.gcd(12, 18), math.lcm(4, 6))
print(mint.isqrt is math.isqrt, mint.gcd is math.gcd)
print(sorted(n for n in dir(mint) if not n.startswith("_")))

vals = [0.1] * 10
print(sum(vals), math.fsum(vals), sum(vals) == 1.0)
print(0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
print(math.nextafter(1.0, 2.0) - 1.0)

print(Decimal("0.1") + Decimal("0.2"), Fraction(1, 3) + Fraction(1, 6))

data = [2, 4, 4, 4, 5, 5, 7, 9]
print(statistics.mean(data), statistics.median(data),
      statistics.mode(data), statistics.pstdev(data))
print(statistics.quantiles(data, n=4))
