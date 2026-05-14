from pathlib import Path

from atptour.cli import configure_logging


def test_configure_logging_writes_error_file(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "atptour.log"

    configure_logging(log_file)

    try:
        raise RuntimeError("boom")
    except RuntimeError:
        import logging

        logging.getLogger("atptour.test").exception("failed to fetch")

    log_text = log_file.read_text()
    assert "ERROR" in log_text
    assert "failed to fetch" in log_text
    assert "RuntimeError: boom" in log_text
