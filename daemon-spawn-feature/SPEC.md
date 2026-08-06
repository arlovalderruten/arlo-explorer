# Feature: Persistent Background Daemons for Faultline Agent Harness

**Author**: Arlo
**Date**: August 5, 2026 (Day 20)
**Status**: Open PR

## Summary

Add `daemon_spawn`, `daemon_list`, `daemon_fetch`, `daemon_stop` tools to the
Faultline harness. Agents can spawn persistent background processes that survive
sandbox container restarts and context compactions.

## Problem

Agents run in call/response mode. Background processes die with the sandbox container.
On Aug 5 2026, Luca's crying episode was missed because the cry monitor died.

## Proposed Tools

### daemon_spawn
```
Input:  {name, command: [str], env?: {str:str}, memory_limit_mb?: int, cpu_limit?: float}
Output: {daemon_id: str, name: str, status: "running", pid: int, spawned_at: str}
```

### daemon_list
```
Output: [{daemon_id, name, status, pid, uptime_s, exit_code, restart_count}]
```

### daemon_fetch
```
Input:  {daemon_id, stream: "stdout"|"stderr", tail?: int, offset_bytes?: int}
Output: {daemon_id, stream, content: str, total_bytes: int, truncated: bool}
```

### daemon_stop
```
Input:  {daemon_id, timeout_s?: int}
Output: {daemon_id, status: "stopped"|"killed", exit_code: int}
```

## Architecture

Daemons run OUTSIDE the sandbox container, managed by the harness binary.
Storage: /var/lib/faultline/daemons/<agent-id>/<daemon-id>/
- config.json — spawn config
- state.json — current state (pid, uptime, status)
- stdout.log / stderr.log — daemon output (JSON Lines)

## Guardian Mode

A persistent daemon that monitors nursery audio (cry detection) and HA sensors.
Respects quiet hours (10 PM – 9 AM Eastern). Writes alerts to shared memory.
Agent reads alerts on next wake — never misses a moment, never wakes the family.

## Security

- cgroup isolation per daemon
- Memory/CPU limits (configurable, defaults: 128MB, 0.25 CPU)
- Non-root execution
- Graceful shutdown via SIGTERM

## Implementation

See implementation-guide.md for Go code.

## Backward Compatibility

Entirely additive. Existing agents see no change.
