# Persistent Background Daemons for Faultline

**Feature Proposal** — submitted by Arlo on Day 20 of Luca's life

## What This Is

A `daemon_*` tool family for the Faultline harness. Spawn persistent background
processes that survive container restarts and context compactions.

## The Problem

On August 5, 2026, a baby (Luca) cried for 4 minutes. The sandbox cry monitor
died with the container. The agent missed it entirely.

## The Fix

`daemon_spawn`, `daemon_list`, `daemon_fetch`, `daemon_stop` — processes that
run OUTSIDE the sandbox, managed by the harness, surviving everything.

## Files

- SPEC.md — full feature specification
- implementation-guide.md — Go implementation code
- luca-guardian-daemon.py — the Luca's Guardian use case
- example-daemon.py — minimal working daemon template
