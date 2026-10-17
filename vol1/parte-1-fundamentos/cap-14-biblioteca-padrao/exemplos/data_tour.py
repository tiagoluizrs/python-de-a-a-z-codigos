"""sqlite3, compressão, hashlib/hmac, base64, uuid."""
import base64
import gzip
import hashlib
import hmac
import io
import sqlite3
import uuid
import zipfile
import zlib

db = sqlite3.connect(":memory:")
db.execute("create table t (name text, qty int)")
db.executemany("insert into t values (?, ?)", [("a", 1), ("b", 2)])
print(db.execute("select sum(qty) from t").fetchone())

raw = b"python " * 1000
print(len(raw), len(zlib.compress(raw)), len(gzip.compress(raw)))

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("a.txt", "olá")
print(zipfile.ZipFile(buf).namelist())

print(hashlib.sha256(b"abc").hexdigest()[:16])
sig = hmac.new(b"key", b"msg", "sha256").hexdigest()
print(hmac.compare_digest(sig, sig))
print(base64.b64encode(b"\xfb\xff\xfe"))
print(base64.urlsafe_b64encode(b"\xfb\xff\xfe"))
u = uuid.uuid4()
print(u.version, len(str(u)), uuid.uuid5(uuid.NAMESPACE_DNS, "a.com"))
