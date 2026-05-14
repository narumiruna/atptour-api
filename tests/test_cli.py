import logging
from pathlib import Path

from typer.testing import CliRunner

from atptour import cli
from atptour.cli import app
from atptour.cli import configure_logging
from atptour.models import LiveMatchesResponse
from tests.test_live import DATA_DIR

runner = CliRunner()


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


def test_configure_logging_rotates_error_file(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "atptour.log"

    configure_logging(log_file, max_bytes=120, backup_count=1)

    log = logging.getLogger("atptour.test")
    for index in range(10):
        log.error("large failure entry %s %s", index, "x" * 80)

    assert log_file.exists()
    assert log_file.with_name("atptour.log.1").exists()


def test_cli_fetches_all_levels_once(monkeypatch, tmp_path: Path) -> None:
    payload = (DATA_DIR / "livematches_tour.json").read_text()
    response = LiveMatchesResponse.model_validate_json(payload)
    levels = []

    def fake_fetch_live_matches(level, *, timeout):
        levels.append((level, timeout))
        return response

    monkeypatch.setattr(cli, "fetch_live_matches", fake_fetch_live_matches)

    result = runner.invoke(
        app,
        [
            "--level",
            "all",
            "--once",
            "--timeout",
            "7",
            "--log-file",
            str(tmp_path / "atptour.log"),
        ],
    )

    assert result.exit_code == 0
    assert levels == [("tour", 7.0), ("challenger", 7.0)]
    assert "ATP Tour Live Matches" in result.stdout
