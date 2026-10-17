"""Verificação de certificados: o padrão é seguro; desligá-la é um erro comum."""
import ssl

context = ssl.create_default_context()
print("padrão: check_hostname =", context.check_hostname, "| verify_mode =", context.verify_mode.name)

unsafe = ssl.create_default_context()
unsafe.check_hostname = False
unsafe.verify_mode = ssl.CERT_NONE
print("desligado:", unsafe.check_hostname, unsafe.verify_mode.name, "-> aceita QUALQUER certificado (vulnerável a interceptação)")
print("versão mínima do TLS:", context.minimum_version.name)
