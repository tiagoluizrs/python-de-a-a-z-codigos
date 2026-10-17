import asyncio
import io
import json
import logging
import logging.config
import threading

import pytest


@pytest.fixture
def clean_loggers():
    created = []

    def make(name):
        logger = logging.getLogger(name)
        created.append(logger)
        return logger

    yield make
    for logger in created:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        logger.filters.clear()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True


def test_configure_logging_basic(load_exercise, clean_loggers):
    configure = load_exercise("ex01_logger_setup").configure_logging
    clean_loggers("t36.one")
    stream = io.StringIO()
    logger = configure("t36.one", "debug", stream)
    logger.debug("olá %s", "mundo")
    logger.info("fim")
    assert stream.getvalue().splitlines() == ["DEBUG t36.one: olá mundo", "INFO t36.one: fim"]
    assert logger.propagate is False and logger.level == logging.DEBUG


def test_configure_logging_is_idempotent(load_exercise, clean_loggers):
    configure = load_exercise("ex01_logger_setup").configure_logging
    clean_loggers("t36.two")
    first, second = io.StringIO(), io.StringIO()
    configure("t36.two", "INFO", first)
    logger = configure("t36.two", logging.WARNING, second)
    assert len(logger.handlers) == 1
    logger.info("descartada")
    logger.warning("vai para o segundo")
    assert first.getvalue() == "" and second.getvalue() == "WARNING t36.two: vai para o segundo\n"
    with pytest.raises(ValueError):
        configure("t36.two", "barulhento")


def make_record(msg="olá %s", args=("mundo",), created=0.0, exc_info=None, **extra):
    record = logging.LogRecord("app.x", logging.WARNING, "f.py", 3, msg, args, exc_info)
    record.created = created
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter(load_exercise):
    formatter = load_exercise("ex02_json_formatter").JsonFormatter()
    line = formatter.format(make_record(user="ana", total=9.5, note="ação"))
    assert "\n" not in line
    data = json.loads(line)
    assert list(data) == ["time", "level", "logger", "message", "note", "total", "user"]
    assert data["time"] == "1970-01-01T00:00:00.000Z" and data["level"] == "WARNING"
    assert data["logger"] == "app.x" and data["message"] == "olá mundo" and data["note"] == "ação"
    assert "ação" in line                                      # ensure_ascii=False
    assert json.loads(formatter.format(make_record(created=1.5)))["time"] == "1970-01-01T00:00:01.500Z"


def test_json_formatter_exception_and_unserializable(load_exercise):
    formatter = load_exercise("ex02_json_formatter").JsonFormatter()
    try:
        1 / 0
    except ZeroDivisionError:
        import sys
        record = make_record(exc_info=sys.exc_info(), obj=object, items={1, 2})
    data = json.loads(formatter.format(record))
    assert "ZeroDivisionError" in data["exc"] and list(data)[-1] == "exc"
    assert data["obj"].startswith("<class") and isinstance(data["items"], str)


def test_redact_filter(load_exercise):
    redact = load_exercise("ex03_filters").RedactFilter(keys=("password", "token"))
    cases = [
        ("login ok password=abc123 user=ana", (), "login ok password=*** user=ana"),
        ("Password: s3cr3t!", (), "Password=***"),
        ('PASSWORD = "a b c" fim', (), "PASSWORD=*** fim"),
        ("token=%s e %s", ("xyz", "ok"), "token=*** e ok"),
        ("mypassword=x sem mudança", (), "mypassword=x sem mudança"),
    ]
    for message, args, expected in cases:
        record = make_record(message, args)
        assert redact.filter(record) is True
        assert record.getMessage() == expected and record.args == ()


def test_level_range_filter(load_exercise):
    module = load_exercise("ex03_filters")
    only_info = module.LevelRangeFilter(logging.INFO, logging.INFO)
    warn_up = module.LevelRangeFilter(logging.WARNING)
    for level, expected_info, expected_warn in [(10, False, False), (20, True, False), (30, False, True), (50, False, True)]:
        record = make_record()
        record.levelno = level
        assert only_info.filter(record) is expected_info and warn_up.filter(record) is expected_warn


def test_log_context_and_filter(load_exercise):
    module = load_exercise("ex04_context")
    flt = module.ContextFilter()
    record = make_record()
    flt.filter(record)
    assert record.request_id == "-"
    with module.log_context(request_id="r1", user="ana"):
        with module.log_context(user="bia", step=2):
            record = make_record()
            assert flt.filter(record) is True
            assert (record.request_id, record.user, record.step) == ("r1", "bia", 2)
        record = make_record()
        flt.filter(record)
        assert record.user == "ana" and not hasattr(record, "step")
    assert module.CONTEXT.get() == {}
    record = make_record(user="original")
    with module.log_context(user="contexto"):
        flt.filter(record)
    assert record.user == "original"                          # não sobrescreve


def test_log_context_resets_on_error_and_isolates(load_exercise):
    module = load_exercise("ex04_context")
    with pytest.raises(RuntimeError):
        with module.log_context(request_id="x"):
            raise RuntimeError
    assert module.CONTEXT.get() == {}
    seen = {}
    with module.log_context(request_id="main"):
        thread = threading.Thread(target=lambda: seen.update(thread=dict(module.CONTEXT.get())))
        thread.start()
        thread.join()

    async def task(rid):
        with module.log_context(request_id=rid):
            await asyncio.sleep(0.01)
            return module.CONTEXT.get()["request_id"]

    async def main():
        return await asyncio.gather(task("a"), task("b"), task("c"))

    assert seen["thread"] == {} and asyncio.run(main()) == ["a", "b", "c"]


def test_duplicate_filter(load_exercise, clean_loggers):
    DuplicateFilter = load_exercise("ex05_dedup_filter").DuplicateFilter
    now = [0.0]
    flt = DuplicateFilter(window=5.0, clock=lambda: now[0])
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(flt)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = clean_loggers("t36.dedup")
    logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.warning("disco cheio")
    for t in (1, 2, 4.9):
        now[0] = t
        logger.warning("disco cheio")
    logger.warning("outra coisa")
    now[0] = 6.0
    logger.warning("disco cheio")
    logger.error("disco cheio")                                # nível diferente: outra mensagem
    now[0] = 20.0
    logger.warning("disco cheio")
    assert stream.getvalue().splitlines() == [
        "disco cheio", "outra coisa", "disco cheio (+3 repetidas)", "disco cheio", "disco cheio"]


def test_build_config_shape(load_exercise, tmp_path):
    build_config = load_exercise("ex06_dict_config").build_config
    config = build_config("t36app", "debug")
    assert config["version"] == 1 and config["disable_existing_loggers"] is False
    assert list(config["handlers"]) == ["console"] and config["root"] == {"level": "WARNING", "handlers": ["console"]}
    assert config["loggers"]["t36app"] == {"level": "DEBUG", "handlers": ["console"], "propagate": False}
    with_file = build_config("t36app", "INFO", tmp_path / "x.log")
    assert list(with_file["handlers"]) == ["console", "file"]
    assert with_file["handlers"]["file"]["maxBytes"] == 1_000_000 and with_file["handlers"]["file"]["backupCount"] == 3
    assert with_file["loggers"]["t36app"]["handlers"] == ["console", "file"]


def test_build_config_applies(load_exercise, tmp_path):
    build_config = load_exercise("ex06_dict_config").build_config
    other = logging.getLogger("t36.other.preexisting")
    path = tmp_path / "app.log"
    try:
        logging.config.dictConfig(build_config("t36applied", "INFO", path))
        assert other.disabled is False
        logger = logging.getLogger("t36applied.sub")
        logger.info("para o arquivo")
        logger.debug("descartada")
        parent = logging.getLogger("t36applied")
        assert parent.propagate is False and {type(h).__name__ for h in parent.handlers} == {
            "StreamHandler", "RotatingFileHandler"}
        for handler in parent.handlers:
            handler.flush()
        text = path.read_text(encoding="utf-8")
        assert "INFO t36applied.sub: para o arquivo" in text and "descartada" not in text
    finally:
        parent = logging.getLogger("t36applied")
        for handler in list(parent.handlers):
            parent.removeHandler(handler)
            handler.close()
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)
            handler.close()
