# Luca Cry Monitor

RTSP audio listener for the Tapo C120 nursery camera via go2rtc.
Monitors audio from `rtsp://192.168.1.199:8554/nursery`, detects crying via RMS amplitude, logs events.

## Requirements
- Python 3 (stdlib only — no pip needed)
- Access to `rtsp://192.168.1.199:8554/nursery` (go2rtc on home network)

## Usage

### On-demand listening session (5 minutes)
```
python3 luca_cry_daemon.py
```
Results saved to:
- `/output/cry_events.json` — list of crying events
- `/output/cry_status.json` — live status (baseline RMS, threshold, state)
- `/output/cry_monitor.log` — log file

### Test mode (30 seconds)
```
python3 luca_cry_test.py
```

### Launch as background daemon
```
python3 start_cry_monitor.py
```

### Check results
```
python3 check_monitor.py
```

## How it works
1. Connects to RTSP stream via TCP interleaved mode
2. Decodes G.711 A-law audio (PCMA/8000) to PCM samples
3. Computes RMS amplitude per audio packet
4. Calibrates baseline over 20s (accounts for white noise machine)
5. Detects crying when RMS exceeds 2x baseline
6. Logs cry events with timestamp, duration, peak RMS

## Audio stream info
- Camera: TP-Link Tapo C120
- RTSP via: go2rtc on `rtsp://192.168.1.199:8554/nursery`
- Codec: G.711 A-law (PCMA), 8kHz, mono
- Video: H.264 (not used by this tool)
