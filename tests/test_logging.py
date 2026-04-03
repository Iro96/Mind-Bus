import logging

from observability.logging import clear_request_context, init_logging, set_request_context


def test_init_logging_formats_child_logger_without_request_context(capsys):
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_level = root.level

    try:
        clear_request_context()
        init_logging()

        logging.getLogger("tests.startup").info("startup log without context")

        captured = capsys.readouterr()
        assert "startup log without context" in captured.err
        assert "[request=unknown" in captured.err
        assert "[model=unknown prompt=unknown]" in captured.err
    finally:
        root.handlers = old_handlers
        root.setLevel(old_level)
        clear_request_context()


def test_init_logging_preserves_explicit_request_context(capsys):
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_level = root.level

    try:
        init_logging()
        set_request_context(
            request_id="req-123",
            thread_id=42,
            model_version="gpt-test",
            prompt_version="prompt-v1",
        )

        logging.getLogger("tests.request").info("request scoped log")

        captured = capsys.readouterr()
        assert "[request=req-123 thread=42]" in captured.err
        assert "[model=gpt-test prompt=prompt-v1]" in captured.err
    finally:
        root.handlers = old_handlers
        root.setLevel(old_level)
        clear_request_context()
