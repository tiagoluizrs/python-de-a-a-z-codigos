"""Exercício 3: conversor snake_case <-> camelCase."""


def to_snake(name: str) -> str:
    """Converta camelCase/PascalCase em snake_case.

    Siglas contam como uma palavra só::

        to_snake("userName") == "user_name"
        to_snake("HTTPServerError") == "http_server_error"
        to_snake("getHTTPResponseCode") == "get_http_response_code"
        to_snake("already_snake") == "already_snake"
        to_snake("version2Beta") == "version2_beta"
        to_snake("") == ""

    Dica: uma letra maiúscula inicia uma nova palavra quando vem depois
    de minúscula/dígito, ou quando vem depois de maiúscula E antes de
    minúscula (o ``S`` de ``HTTPServer``). Sem regex: percorra com índices.
    """
    raise NotImplementedError


def to_camel(name: str, pascal: bool = False) -> str:
    """Converta snake_case em camelCase (ou PascalCase com ``pascal=True``).

        to_camel("user_name") == "userName"
        to_camel("user_name", pascal=True) == "UserName"
        to_camel("__private_value") == "privateValue"
        to_camel("a__b") == "aB"
        to_camel("") == ""
    """
    raise NotImplementedError
