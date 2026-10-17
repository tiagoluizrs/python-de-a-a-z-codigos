"""Exercício 1: interpretar uma URL de conexão (Capítulo 12 do Volume 3) sem biblioteca."""


def parse_mysql_url(url):
    """Interpreta ``mysql://usuario:senha@host:porta/banco?charset=utf8mb4&connect_timeout=5``.

    Devolve um dicionário com ``user``, ``password``, ``host``, ``port`` (int), ``database``
    e as opções da consulta (``charset`` etc.; números inteiros viram ``int``).

    * esquemas aceitos: ``mysql``, ``mariadb`` e ``mysql+pymysql``; outro levanta ``ValueError``;
    * ``port`` padrão 3306; ``password`` ausente vira ``""``; ``user`` ausente levanta ``ValueError``;
    * usuário e senha são decodificados de percent-encoding (``p%40ss`` -> ``p@ss``);
    * ``host`` ausente ou ``database`` ausente levantam ``ValueError``;
    * ``charset`` padrão ``utf8mb4`` quando não vier na consulta."""
    raise NotImplementedError
