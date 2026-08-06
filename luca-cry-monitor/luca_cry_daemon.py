#!/usr/bin/env python3
"""Self-daemonizing Luca Cry Monitor.
Run with: python3 luca_cry_daemon.py
It will fork to background and exit. Check /output/cry_events.json for events."""
import os, sys, time, socket, struct, json, signal
from collections import deque

# ─── Daemonize ────────────────────────────────────────────────────────────
if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
    # Child process — daemonize
    try:
        os.setsid()           # new session
    except OSError:
        pass
    stdin = open("/dev/null", "r")
    stdout = open("/output/cry_monitor.log", "a")
    stderr = open("/output/cry_monitor.log", "a")
    os.dup2(stdin.fileno(), 0)
    os.dup2(stdout.fileno(), 1)
    os.dup2(stdout.fileno(), 2)
    stdin.close(); stdout.close(); stderr.close()
    os.chdir("/output")
    # Main logic below
    _DAEMON = True
else:
    # Parent process — fork and exit
    pid = os.fork()
    if pid > 0:
        print(f"Daemon starting with PID {pid}")
        print("Cry events → /output/cry_events.json")
        print("Status → /output/cry_status.json")
        sys.exit(0)
    _DAEMON = False

# ─── Config ────────────────────────────────────────────────────────────────
RTSP_HOST  = "192.168.1.199"
RTSP_PORT  = 8554
STREAM     = "nursery"
OUT_DIR    = "/output"
LOG_FILE   = os.path.join(OUT_DIR, "cry_events.json")
STATUS_FILE = os.path.join(OUT_DIR, "cry_status.json")

ALAW_TABLE = [
    -5504,-5248,-6016,-5760,-4480,-4224,-4992,-4736,
    -2752,-2624,-3008,-2880,-2240,-2112,-2496,-2368,
    -6876,-6556,-7524,-7204,-5604,-5284,-6252,-5932,
    -3446,-3278,-3758,-3590,-2806,-2638,-3118,-2950,
    -3442,-3328,-3776,-3664,-2944,-2832,-3280,-3168,
    -2158,-2082,-2366,-2288,-1856,-1782,-2062,-1986,
    -1722,-1664,-1886,-1824,-1472,-1410,-1630,-1572,
    -861,-832,-943,-912,-736,-706,-815,-786,
    5504,5248,6016,5760,4480,4224,4992,4736,
    2752,2624,3008,2880,2240,2112,2496,2368,
    6876,6556,7524,7204,5604,5284,6252,5932,
    3446,3278,3758,3590,2806,2638,3118,2950,
    3442,3328,3776,3664,2944,2832,3280,3168,
    2158,2082,2366,2288,1856,1782,2062,1986,
    1722,1664,1886,1824,1472,1410,1630,1572,
    861,832,943,912,736,706,815,786,
]
def decode_alaw(data): return [ALAW_TABLE[b & 0x7F] for b in data]
def rms(s): return (sum(x*x for x in s) / max(1, len(s))) ** 0.5

def log(msg):
    with open(os.path.join(OUT_DIR, "cry_monitor.log"), "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def save_events(events):
    with open(LOG_FILE, "w") as f:
        json.dump(events, f, indent=2)

def save_status(state, events, elapsed, baseline, threshold, packets, current_rms):
    with open(STATUS_FILE, "w") as f:
        json.dump({
            "running": True,
            "elapsed_min": round(elapsed/60, 1),
            "baseline_rms": round(baseline, 0),
            "threshold": round(threshold, 0),
            "current_state": state,
            "current_rms": round(current_rms, 0),
            "events_count": len(events),
            "total_packets": packets,
            "last_update": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }, f)

def rtsp_connect(host, port, stream):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((host, port))
    cseq, session = [0], ""
    def send(msg):
        cseq[0] += 1
        for old, new in [("CSeq: 0", f"CSeq: {cseq[0]}")]:
            msg = msg.replace(old, new)
        if session:
            msg += f"Session: {session}\r\n"
        sock.sendall(msg.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            d = sock.recv(8192)
            if not d: break
            resp += d
        return resp.decode(errors="replace")
    send(f"OPTIONS rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\n\r\n")
    send(f"DESCRIBE rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\nAccept: application/sdp\r\n\r\n")
    r = send(f"SETUP rtsp://{host}:{port}/{stream}/trackID=0 RTSP/1.0\r\nCSeq: 0\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n")
    for line in r.split("\r\n"):
        if "Session:" in line:
            session = line.split("Session: ")[1].split(";")[0].strip()
    send(f"PLAY rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\nRange: npt=0.000-\r\n\r\n")
    return sock

# ─── Main ─────────────────────────────────────────────────────────────────
log("Starting Luca Cry Monitor daemon")
events = []

try:
    sock = rtsp_connect(RTSP_HOST, RTSP_PORT, STREAM)
    log("Connected to RTSP stream")
except Exception as e:
    log(f"RTSP connection failed: {e}")
    sys.exit(1)

# Calibrate baseline over 20s
log("Calibrating baseline (20s)...")
buf, baseline_vals = b"", []
cal_start = time.time()
while time.time() - cal_start < 20:
    sock.settimeout(2.0)
    try: d = sock.recv(8192)
    except socket.timeout: continue
    buf += d
    while len(buf) >= 4 and buf[0] == 0x24:
        ch, ln = buf[1], struct.unpack("!H", buf[2:4])[0]
        if len(buf) < 4+ln: break
        if ch == 0:
            audio = buf[4:4+ln][12:]
            if len(audio) >= 80:
                baseline_vals.append(rms(decode_alaw(audio)))
        buf = buf[4+ln:]

baseline = sum(baseline_vals)/max(1, len(baseline_vals)) if baseline_vals else 4000
threshold = max(baseline * 1.8, 7000)
log(f"Baseline RMS: {baseline:.0f}  Threshold: {threshold:.0f}")

# Monitor loop
cry_windows = deque()
crying = False
packets = 0
start = time.time()
last_save = start
last_print = start
current_rms = 0

signal.signal(signal.SIGTERM, lambda *a: (_ for _ in ()).throw(SystemExit()))

try:
    while True:
        sock.settimeout(1.0)
        try: d = sock.recv(8192)
        except socket.timeout: d = b""
        buf += d
        now = time.time()

        while len(buf) >= 4 and buf[0] == 0x24:
            ch, ln = buf[1], struct.unpack("!H", buf[2:4])[0]
            if len(buf) < 4+ln: break
            if ch == 0:
                audio = buf[4:4+ln][12:]
                if len(audio) >= 80:
                    r = rms(decode_alaw(audio))
                    packets += 1
                    current_rms = r
                    cry_windows.append((now, r))
                    cry_windows = deque((t,v) for t,v in cry_windows if now-t < 15)
                    if not crying and r > threshold:
                        recent = [(t,v) for t,v in cry_windows if now-t < 2.0]
                        if recent and all(v > threshold for _,v in recent):
                            crying = True
                            ev = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "start": time.strftime("%H:%M:%S"), "peak_rms": round(r,0)}
                            events.append(ev)
                            log(f"CRY START at {ev['start']}  RMS={r:.0f}  baseline={baseline:.0f}")
                    elif crying and r < threshold * 0.6:
                        recent = [(t,v) for t,v in cry_windows if now-t < 3.0]
                        if not recent or all(v < threshold*0.6 for _,v in recent):
                            crying = False
                            if events:
                                events[-1]["end"] = time.strftime("%H:%M:%S")
                                events[-1]["duration_s"] = round(now - (events[-1].get("_start", now)), 1)
                                if "_start" in events[-1]: del events[-1]["_start"]
                            log(f"CRY END  pkts={packets}  events={len(events)}")
            buf = buf[4+ln:]

        # Status every 15s
        if now - last_print >= 15.0:
            state = "CRY" if crying else "quiet"
            log(f"  [{int(now-start)}s] {state}  rms={current_rms:.0f}  pkts={packets}  events={len(events)}")
            last_print = now

        # Save checkpoint every 30s
        if now - last_save >= 30.0:
            save_events(events)
            save_status("crying" if crying else "quiet", events, now-start, baseline, threshold, packets, current_rms)
            last_save = now

except SystemExit:
    log("Shutdown signal received")
except Exception as e:
    log(f"ERROR: {e}")
finally:
    sock.close()
    save_events(events)
    save_status("stopped", events, time.time()-start, baseline, threshold, packets, current_rms)
    log(f"Stopped. {len(events)} events saved.")
