#!/usr/bin/env python3
"""
Luca Cry Monitor — 30-second diagnostic test.
Runs for 30s, prints RTSP status and audio RMS readings, then exits.
"""
import socket, struct, time, os, json, sys, threading
from collections import deque

RTSP_HOST = "192.168.1.199"
RTSP_PORT = 8554
STREAM    = "nursery"
OUT_DIR   = "/output"
TEST_SECS = 30

ALAW_TABLE = [
    -5504, -5248, -6016, -5760, -4480, -4224, -4992, -4736,
    -2752, -2624, -3008, -2880, -2240, -2112, -2496, -2368,
    -6876, -6556, -7524, -7204, -5604, -5284, -6252, -5932,
    -3446, -3278, -3758, -3590, -2806, -2638, -3118, -2950,
    -3442, -3328, -3776, -3664, -2944, -2832, -3280, -3168,
    -2158, -2082, -2366, -2288, -1856, -1782, -2062, -1986,
    -1722, -1664, -1886, -1824, -1472, -1410, -1630, -1572,
    -861,  -832,  -943,  -912,  -736,  -706,  -815,  -786,
    5504,   5248,   6016,   5760,   4480,   4224,   4992,   4736,
    2752,   2624,   3008,   2880,   2240,   2112,   2496,   2368,
    6876,   6556,   7524,   7204,   5604,   5284,   6252,   5932,
    3446,   3278,   3758,   3590,   2806,   2638,   3118,   2950,
    3442,   3328,   3776,   3664,   2944,   2832,   3280,   3168,
    2158,   2082,   2366,   2288,   1856,   1782,   2062,   1986,
    1722,   1664,   1886,   1824,   1472,   1410,   1630,   1572,
    861,    832,    943,    912,    736,    706,    815,    786,
]

def decode_alaw(data: bytes) -> list:
    return [ALAW_TABLE[b & 0x7F] for b in data]

def rms(samples: list) -> float:
    if not samples:
        return 0.0
    return (sum(s * s for s in samples) / len(samples)) ** 0.5

def rtsp_connect(host, port, stream):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))
    cseq = [0]

    def send(sock, msg):
        cseq[0] += 1
        for old, new in [("CSeq: 0", f"CSeq: {cseq[0]}")]:
            msg = msg.replace(old, new)
        msg += f"Session: {session}\r\n" if session else ""
        sock.sendall(msg.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            d = sock.recv(4096)
            if not d:
                break
            resp += d
        return resp.decode(errors="replace")

    session = ""

    r = send(sock, f"OPTIONS rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\n\r\n")
    print("OPTIONS:", "200 OK" in r)

    r = send(sock, f"DESCRIBE rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\nAccept: application/sdp\r\n\r\n")
    print("DESCRIBE:", "200 OK" in r)
    print("SDP:", r[:400])

    r = send(sock, f"SETUP rtsp://{host}:{port}/{stream}/trackID=0 RTSP/1.0\r\nCSeq: 0\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n")
    print("SETUP audio:", "200 OK" in r)
    for line in r.split("\r\n"):
        if "Session" in line:
            session = line.split("Session: ")[1].split(";")[0].strip()
            print("Session:", session)

    r = send(sock, f"PLAY rtsp://{host}:{port}/{stream} RTSP/1.0\r\nCSeq: 0\r\nRange: npt=0.000-\r\n\r\n")
    print("PLAY:", "200 OK" in r)

    return sock, session

def main():
    print(f"=== Luca Cry Monitor Test — {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Testing for {TEST_SECS} seconds...\n")

    sock, session = rtsp_connect(RTSP_HOST, RTSP_PORT, STREAM)
    print()

    events = []
    start = time.time()
    last_print = start
    packets = 0
    max_rms = 0
    rms_vals = []

    buf = b""
    crying = False
    cry_start = None
    cry_threshold = 600

    print("Listening for audio packets...\n")

    while time.time() - start < TEST_SECS:
        try:
            sock.settimeout(2.0)
            d = sock.recv(4096)
        except socket.timeout:
            print("  (no data for 2s)")
            continue

        buf += d

        while len(buf) >= 4 and buf[0] == 0x24:
            channel = buf[1]
            length = struct.unpack("!H", buf[2:4])[0]
            if len(buf) < 4 + length:
                break
            rtp = buf[4:4+length]
            buf = buf[4+length:]

            if channel == 0:  # Audio channel
                packets += 1
                if len(rtp) >= 13:
                    audio = rtp[12:]
                    samples = decode_alaw(audio)
                    r = rms(samples)
                    rms_vals.append(r)
                    max_rms = max(max_rms, r)

                    now = time.time()
                    if now - last_print >= 2.0:
                        state = "🔴 CRY" if r > cry_threshold else "🟢 quiet"
                        print(f"  [{int(now-start)}s] {state}  RMS={r:.0f}  pkts={packets}")
                        last_print = now

                    if r > cry_threshold and not crying:
                        crying = True
                        cry_start = now
                        events.append({"type": "cry_start", "time": now - start, "rms": r})
                        print(f"\n⚠️  CRY START at {int(now-start)}s, RMS={r:.0f}\n")
                    elif r < cry_threshold * 0.5 and crying:
                        crying = False
                        events.append({"type": "cry_end", "time": now - start, "rms": r, "duration": now - cry_start})
                        print(f"✅  Cry ended at {int(now-start)}s\n")

        if len(buf) > 10000:
            buf = buf[-500:]  # prevent memory bloat

    sock.close()

    # Summary
    print(f"\n=== Test Complete ===")
    print(f"Duration: {TEST_SECS}s")
    print(f"Audio packets received: {packets}")
    print(f"Max RMS: {max_rms:.0f}")
    if rms_vals:
        print(f"Avg RMS: {sum(rms_vals)/len(rms_vals):.0f}")
    print(f"Events: {json.dumps(events, indent=2)}")

    # Save events
    out = os.path.join(OUT_DIR, "cry_events.json")
    with open(out, "w") as f:
        json.dump({
            "test_run": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_s": TEST_SECS,
            "packets": packets,
            "max_rms": max_rms,
            "avg_rms": round(sum(rms_vals)/len(rms_vals), 1) if rms_vals else 0,
            "events": events,
        }, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    main()
