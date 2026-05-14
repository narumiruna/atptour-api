# ATP Tour API

Terminal watcher for ATP Tour and ATP Challenger live match scores.

## Usage

Fetch once:

```bash
just tour-once
just challenger-once
just all-once
```

Watch every 15 seconds:

```bash
just watch-tour
just watch-challenger
just watch-all
```

Run the CLI directly:

```bash
uv run atptour --level tour --once
uv run atptour --level all --interval 15 --timeout 30
```

Supported levels are `tour`, `challenger`, and `all`.

## Logging

Fetch failures are logged to `logs/atptour.log` by default. The log file rotates at 5 MB and keeps 5 backups.

Use `--log-file` to write failures somewhere else:

```bash
uv run atptour --level tour --log-file /tmp/atptour.log
```

## Source

The live score endpoint used by the ATP website is:

```text
https://app.atptour.com/api/v2/gateway/livematches/website?scoringTournamentLevel=<tour|challenger>
```

The ATP scores page exposes a `cmsPollInterval` value of `15`, so the watcher defaults to polling every 15 seconds.
