# ATP Tour API 🎾

Terminal watcher for ATP Tour and ATP Challenger live match scores.

It uses the same live score API that the ATP scores page calls, renders the response with Rich, and defaults to the 15-second polling interval exposed by the page.

## ✨ Features

- Fetch ATP Tour live matches.
- Fetch ATP Challenger live matches.
- Fetch both levels in one run with `--level all`.
- Poll every 15 seconds by default.
- Reuse a `curl_cffi` session with Chrome impersonation.
- Log fetch failures to a rotating file by default.
- Parse responses with Pydantic models backed by captured API samples.

## ✅ Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/) for the documented task shortcuts

## ⚙️ Setup

```bash
uv sync
```

## 🚀 Usage

Fetch once and exit:

```bash
just tour-once
just challenger-once
just all-once
```

Watch live scores:

```bash
just watch-tour
just watch-challenger
just watch-all
```

The watch commands keep running and poll every 15 seconds.

## 🧰 CLI

Run the CLI directly when you need custom options:

```bash
uv run atptour --level tour --once
uv run atptour --level challenger --once
uv run atptour --level all --interval 15 --timeout 30
```

Options:

| Option | Default | Description |
| --- | --- | --- |
| `--level` | `tour` | `tour`, `challenger`, or `all`. |
| `--once` | `false` | Fetch once and exit instead of watching forever. |
| `--interval` | `15.0` | Seconds between fetches in watch mode. |
| `--timeout` | `30.0` | HTTP request timeout in seconds. |
| `--log-file` | `logs/atptour.log` | File path for fetch failure logs. |

## 📝 Logging

Fetch failures are logged to `logs/atptour.log` by default. The log file rotates at 5 MB and keeps 5 backups.

Failure logs include:

- tournament level
- consecutive failure count
- HTTP status code when available
- request timeout
- response text snippet when available
- stack trace

Use `--log-file` to write failures somewhere else:

```bash
uv run atptour --level tour --log-file /tmp/atptour.log
```

Runtime logs are ignored by git.

## 🔎 Data Source

The live score endpoint used by the ATP website is:

```text
https://app.atptour.com/api/v2/gateway/livematches/website?scoringTournamentLevel=<tour|challenger>
```

The ATP scores page exposes:

```text
cmsPollInterval = 15
```

That is why this watcher defaults to polling every 15 seconds.

## 🛠️ Development

Run the full local gate:

```bash
just all
```

Individual checks:

```bash
just format
just lint
just type
just test
```

Captured API samples live in `tests/data/` and are used by the model and renderer tests.
