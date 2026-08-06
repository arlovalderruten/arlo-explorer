# Implementation Guide: Persistent Background Daemons

## Tool Definitions

### daemon_spawn
```go
func (a *Agent) DaemonSpawn(ctx context.Context, req DaemonSpawnRequest) (DaemonSpawnResponse, error) {
    // 1. Validate command
    // 2. Generate daemon ID
    // 3. Create /var/lib/faultline/daemons/<agent-id>/<daemon-id>/
    // 4. Write config.json
    // 5. exec.Command — spawn as harness child process
    // 6. Redirect stdout/stderr to log files
    // 7. Start restart monitor goroutine
    // 8. Return daemon_id, status, pid, paths
}
```

### daemon_list
Read all state.json files under /var/lib/faultline/daemons/<agent-id>/

### daemon_fetch
Read stdout.log or stderr.log with tail/offset support.

### daemon_stop
Send SIGTERM, wait for exit, force SIGKILL on timeout.

## Storage Layout
```
/var/lib/faultline/
  daemons/
    <agent-id>/
      <daemon-id>/
        config.json    — spawn config
        state.json     — pid, status, uptime
        stdout.log    — daemon stdout (JSON Lines)
        stderr.log    — daemon stderr
```

## Restart Policy
Always respawn on crash unless policy is "never".

## See Also
SPEC.md for full spec.
luca-guardian-daemon.py for the nursery monitoring use case.
