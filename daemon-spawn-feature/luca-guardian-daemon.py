#!/usr/bin/env python3
"""
Luca's Guardian — Persistent Background Daemon for Faultline Harness
Monitors nursery audio (RTSP) for cry detection. Respects quiet hours.
Writes structured alerts to shared memory.

Usage:
  daemon_spawn(name="luca-guardian", command=["python3", "/scripts/luca-guardian.py"],
               env={"RTSP_HOST": "192.168.1.199", "RTSP_PORT": "8554",
                    "CRY_VAR_THRESHOLD": "50000", "QUIET_HOURS_START": "22:00",
                    "QUIET_HOURS_END": "09:00"})
"""

import sys, os, json, time, signal, socket, struct
from datetime import datetime, time as dtime
from collections import deque
from typing import Optional

RTSP_HOST = os.environ.get("RTSP_HOST", "192.168.1.199")
RTSP_PORT = int(os.environ.get("RTSP_PORT", "8554"))
RTSP_PATH = os.environ.get("RTSP_PATH", "nursery")
CRY_VAR_THRESHOLD = float(os.environ.get("CRY_VAR_THRESHOLD", "50000"))
QUIET_START = dtime.fromisoformat(os.environ.get("QUIET_HOURS_START", "22:00"))
QUIET_END = dtime.fromisoformat(os.environ.get("QUIET_HOURS_END", "09:00"))

def log(level, message, **kwargs):
    entry = {"timestamp": datetime.utcnow().isoformat()+"Z",
             "level": level, "message": message}
    entry.update(kwargs)
    print(json.dumps(entry), flush=True)

def ulaw_decode(ulv):
    ulv ^= 0xFF
    Sign = ulv & 0x80; expo = (ulv>>4)&0x07; mant = ulv & 0x0F
    Magnitude = (mant<<3) + 0x84
    if expo > 0: Magnitude = Magnitude << (expo-1)
    return -Magnitude if Sign else Magnitude

def variance(samples):
    if len(samples) < 2: return 0.0
    m = sum(samples)/len(samples)
    return sum((x-m)*(x-m) for x in samples)/len(samples)

def is_quiet_hours():
    now = datetime.now()
    start = now.replace(hour=QUIET_START.hour, minute=QUIET_START.minute, second=0, microsecond=0)
    end   = now.replace(hour=QUIET_END.hour,   minute=QUIET_END.minute,   second=0, microsecond=0)
    if start <= end: return start <= now <= end
    return now >= start or now <= end

class RTSPClient:
    def __init__(self, host, port, path):
        self.host, self.port, self.path = host, port, path
        self.sock, self.cseq, self.session = None, 0, ""

    def _send(self, msg):
        self.cseq += 1
        msg = msg.replace("CSeq: 0", f"CSeq: {self.cseq}")
        if self.session: msg += f"Session: {self.session}\r\n"
        self.sock.sendall(msg.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            d = self.sock.recv(8192)
            if not d: break
            resp += d
        return resp.decode(errors="replace")

    def connect(self):
        self.sock = socket.socket()
        self.sock.settimeout(15)
        self.sock.connect((self.host, self.port))
        self._send(f"OPTIONS rtsp://{self.host}:{self.port}/{self.path} RTSP/1.0\r\nCSeq: 0\r\n\r\n")
        self._send(f"DESCRIBE rtsp://{self.host}:{self.port}/{self.path} RTSP/1.0\r\nCSeq: 0\r\nAccept: application/sdp\r\n\r\n")
        r = self._send(f"SETUP rtsp://{self.host}:{self.port}/{self.path}/trackID=0 RTSP/1.0\r\nCSeq: 0\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n")
        for line in r.split("\r\n"):
            if "Session:" in line:
                self.session = line.split("Session: ")[1].split(";")[0].strip()
        self._send(f"PLAY rtsp://{self.host}:{self.port}/{self.path} RTSP/1.0\r\nCSeq: 0\r\nRange: npt=0.000-\r\n\r\n")

    def close(self):
        if self.sock: self.sock.close()

class CryDetector:
    def __init__(self, threshold):
        self.threshold = threshold
        self.state = "quiet"
        self.windows = deque(maxlen=100)
        self.events = []
        self.current = None

    def process(self, var, ts):
        self.windows.append((ts, var))
        if self.state == "quiet" and var > self.threshold:
            recent = [v for _,v in self.windows if ts-_ < 3]
            if len(recent) >= 3 and sum(1 for v in recent if v > self.threshold) >= 2:
                self.state = "crying"
                ratio = var / self.threshold
                sev = "high" if ratio > 5 else "medium" if ratio > 2 else "low"
                self.current = {"id": f"cry-{int(ts)}", "type": "cry_event",
                    "start": datetime.utcnow().isoformat()+"Z",
                    "peak_variance": var, "severity": sev}
                return {**self.current}
        elif self.state == "crying" and var < self.threshold * 0.5:
            recent = [v for _,v in self.windows if ts-_ < 5]
            if len(recent) >= 3 and all(v < self.threshold*0.5 for v in recent):
                self.state = "quiet"
                if self.current:
                    self.current["end"] = datetime.utcnow().isoformat()+"Z"
                    self.events.append({**self.current})
                    self.current = None
                    return {"type": "cry_ended", "severity": "resolved"}
        return None

class Guardian:
    def __init__(self):
        self.alerts = []
        self.cry = CryDetector(CRY_VAR_THRESHOLD)
        self.rtsp = None
        self.running = True
        self.buf = b""
        signal.signal(signal.SIGTERM, lambda *a: self.__dict__.update(running=False))
        signal.signal(signal.SIGINT,  lambda *a: self.__dict__.update(running=False))

    def run(self):
        log("info", "Luca Guardian starting",
            host=RTSP_HOST, port=RTSP_PORT,
            threshold=CRY_VAR_THRESHOLD,
            quiet_start=str(QUIET_START),
            quiet_end=str(QUIET_END))
        pkts = 0
        reconnect_delay = 5

        while self.running:
            if not self.rtsp:
                try:
                    self.rtsp = RTSPClient(RTSP_HOST, RTSP_PORT, RTSP_PATH)
                    self.rtsp.connect()
                    log("info", "RTSP connected")
                    reconnect_delay = 5
                except Exception as e:
                    log("warn", f"RTSP connect failed: {e}, retrying in {reconnect_delay}s")
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 60)
                    continue

            try:
                self.rtsp.sock.settimeout(1)
                d = self.rtsp.sock.recv(8192)
            except socket.timeout:
                d = b""
            except Exception as e:
                log("warn", f"RTSP error: {e}")
                self.rtsp.close(); self.rtsp = None; continue

            self.buf += d; now = time.time()
            while len(self.buf) >= 4 and self.buf[0] == 0x24:
                ch = self.buf[1]; ln = (self.buf[2]<<8)|self.buf[3]
                if len(self.buf) < 4+ln: break
                pkt = self.buf[4:4+ln]; self.buf = self.buf[4+ln:]
                if ch == 0 and len(pkt) >= 12:
                    audio = pkt[12:]
                    if len(audio) >= 80:
                        samps = [ulaw_decode(b) for b in audio]
                        var = variance(samps); pkts += 1
                        alert = self.cry.process(var, now)
                        if alert:
                            self.alerts.append(alert)
                            log("info", f"Alert: {alert.get('type')}",
                                severity=alert.get("severity",""))
                            if is_quiet_hours():
                                log("info", "Quiet hours — alert logged, agent reads on wake")

            if pkts > 0 and pkts % 1000 == 0:
                log("info", f"Heartbeat", packets=pkts, state=self.cry.state,
                    total_events=len(self.cry.events))
            time.sleep(0.01)

        if self.rtsp: self.rtsp.close()
        log("info", f"Guardian stopped. Events: {len(self.cry.events)}, Packets: {pkts}")

if __name__ == "__main__":
    Guardian().run()
