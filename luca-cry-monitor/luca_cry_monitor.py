#!/usr/bin/env python3
"""
Luca Cry Monitor — production version.
Monitors RTSP audio from nursery camera (via go2rtc), detects crying,
logs events to /output/cry_events.json, and prints status.
"""
import socket, struct, time, os, json, sys
from collections import deque

RTSP_HOST  = "192.168.1.199"
RTSP_PORT  = 8554
STREAM     = "nursery"
OUT_DIR    = "/output"
LOG_FILE   = os.path.join(OUT_DIR, "cry_events.json")
STATUS_FILE = os.path.join(OUT_DIR, "cry_status.json")

# ─── G.711 A-law decode ────────────────────────────────────────────────────
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
def decode_alaw(data: bytes):
    return [ALAW_TABLE[b & 0x7F] for b in data]

def rms(samples):
    return (sum(s*s for s in samples) / max(1, len(samples))) ** 0.5

# ─── RTSP via TCP interleaved ─────────────────────────────────────────────
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
            if not d:
                break
            resp += d
        return resp.decode(errors="replace")

    send(f"OPTIONS rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\n\r\n")
    send(f"DESCRIBE rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\nAccept: application/sdp\r\n\r\n")
    r = send(f"SETUP rtsp://{host}:{port}/{stream}/trackID=0 RTSP/1.0\r\nCSeq: 0\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n")
    for line in r.split("\r\n"):
        if "Session:" in line:
            session = line.split("Session: ")[1].split(";")[0].strip()
    send(f"PLAY rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\nRange: npt=0.000-\r\n\r\n")
    return sock, session

# ─── Calibrate baseline (30s of quiet) ────────────────────────────────────
def calibrate(sock, samples_needed=300):
    print("Calibrating baseline (30s quiet)...")
    buf, rms_vals, start = b"", [], time.time()
    while len(rms_vals) < samples_needed and time.time() - start < 35:
        sock.settimeout(3.0)
        try:
            d = sock.recv(4096)
        except socket.timeout:
            continue
        buf += d
        while len(buf) >= 4 and buf[0] == 0x24:
            channel, length = buf[1], struct.unpack("!H", buf[2:4])[0]
            if len(buf) < 4 + length:
                break
            if channel == 0:
                audio = buf[4:4+length][12:]
                if len(audio) >= 80:
                    rms_vals.append(rms(decode_alaw(audio)))
            buf = buf[4+length:]

    if rms_vals:
        baseline = sum(rms_vals) / len(rms_vals)
        noise_floor = sorted(rms_vals)[len(rms_vals)//10]  # 10th percentile
        print(f"  Baseline avg RMS: {baseline:.0f}  noise floor: {noise_floor:.0f}")
        return baseline, noise_floor, rms_vals
    return 4000.0, 3000.0, [4000]

# ─── Main monitor loop ───────────────────────────────────────────────────
def main():
    print(f"=== Luca Cry Monitor — {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    sock, _ = rtsp_connect(RTSP_HOST, RTSP_PORT, STREAM)
    baseline, noise_floor, _ = calibrate(sock)
    
    # Cry threshold = 2x baseline, min 5000 above noise floor
    threshold = max(baseline * 2.0, noise_floor + 5000)
    cry_end_threshold = baseline * 1.3
    min_cry_s = 1.5   # must sustain for this long to count
    cooldown_s = 5.0   # between events

    print(f"\nThreshold: {threshold:.0f} RMS")
    print(f"Monitoring for crying...\n")

    events = []
    buf = b""
    crying = False
    cry_windows = deque()
    last_event = 0
    last_print = time.time()
    packets = 0
    start = time.time()
    running = True

    def parse_and_process():
        nonlocal buf, crying, cry_windows, last_event, last_print, packets
        now = time.time()

        # Pull whatever's available
        sock.settimeout(0.5)
        try:
            d = sock.recv(8192)
            buf += d
        except socket.timeout:
            pass

        while len(buf) >= 4 and buf[0] == 0x24:
            channel, length = buf[1], struct.unpack("!H", buf[2:4])[0]
            if len(buf) < 4 + length:
                break
            if channel == 0:
                audio = buf[4:4+length][12:]
                if len(audio) >= 80:
                    r = rms(decode_alaw(audio))
                    packets += 1
                    cry_windows.append((now, r))
                    # Keep only last 20s
                    cry_windows = deque((t,v) for t,v in cry_windows if now - t < 20)

                    # Detect start
                    if r > threshold and not crying and (now - last_event) > cooldown_s:
                        # Check if sustained
                        recent = [(t,v) for t,v in cry_windows if now - t < min_cry_s]
                        if recent and all(v > threshold for _,v in recent):
                            crying = True
                            cry_start = min(t for t,_ in recent)
                            print(f"\n⚠️  CRY DETECTED at {time.strftime('%H:%M:%S')} | RMS={r:.0f} | baseline={baseline:.0f}")
                            events.append({
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "start_hms": time.strftime("%H:%M:%S"),
                                "start_unix": cry_start,
                                "peak_rms": r,
                            })
                            last_event = now

                    # Detect end
                    elif r < cry_end_threshold and crying:
                        recent = [(t,v) for t,v in cry_windows if now - t < 3.0]
                        if not recent or all(v < cry_end_threshold for _,v in recent):
                            crying = False
                            if events:
                                events[-1]["end_hms"] = time.strftime("%H:%M:%S")
                                events[-1]["end_unix"] = now
                                events[-1]["duration_s"] = round(now - events[-1]["start_unix"], 1)
                                del events[-1]["start_unix"]
                                if "end_unix" in events[-1]:
                                    del events[-1]["end_unix"]
                            print(f"✅  Cry ended — {events[-1].get('duration_s', '?')}s\n")

            buf = buf[4+length:]

        # Status print
        if now - last_print >= 10.0:
            state = "🔴 CRY" if crying else "🟢 quiet"
            elapsed = int(now - start)
            mins = elapsed // 60
            secs = elapsed % 60
            print(f"  [{mins}m{secs:02d}s] {state}  RMS={r if 'r' in dir() else 0:.0f}  pkts={packets}  events={len(events)}")
            last_print = now

        # Save checkpoint
        with open(LOG_FILE, "w") as f:
            json.dump(events, f, indent=2)
        with open(STATUS_FILE, "w") as f:
            json.dump({
                "running": running,
                "elapsed_s": int(time.time() - start),
                "baseline_rms": round(baseline, 0),
                "threshold": round(threshold, 0),
                "current_state": "crying" if crying else "quiet",
                "events_count": len(events),
                "last_update": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }, f)
        return running

    # Main loop
    try:
        while True:
            parse_and_process()
    except KeyboardInterrupt:
        running = False
        print("\nStopped.")
    finally:
        sock.close()
        with open(LOG_FILE, "w") as f:
            json.dump(events, f, indent=2)
        print(f"Saved {len(events)} cry events to {LOG_FILE}")

if __name__ == "__main__":
    main()
