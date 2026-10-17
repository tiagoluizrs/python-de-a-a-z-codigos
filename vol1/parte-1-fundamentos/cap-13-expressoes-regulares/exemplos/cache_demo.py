"""O cache interno de padrões de re.compile/re.search."""
import re
import time

re.purge()
t0 = time.perf_counter()
p1 = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})")
t1 = time.perf_counter()
p2 = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})")
t2 = time.perf_counter()
print("mesmo objeto:", p1 is p2)
print(f"1a chamada {1e6*(t1-t0):.1f} us, 2a {1e6*(t2-t1):.1f} us")
re.purge()
print("depois de purge:", re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})") is p1)

# Flags fazem parte da chave do cache
print(re.compile("a", re.I) is re.compile("a"))
