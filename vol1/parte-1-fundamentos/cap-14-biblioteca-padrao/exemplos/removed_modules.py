"""Quais módulos da PEP 594 e afins ainda existem neste interpretador?"""
import importlib.util

PEP_594 = ("aifc audioop cgi cgitb chunk crypt imghdr mailcap msilib nis "
           "nntplib ossaudiodev pipes sndhdr spwd sunau telnetlib uu "
           "xdrlib").split()
OTHERS = "asyncore asynchat smtpd imp distutils lib2to3".split()

for group in (PEP_594, OTHERS):
    present = [n for n in group if importlib.util.find_spec(n)]
    print(len(group), "verificados; presentes:", present)
