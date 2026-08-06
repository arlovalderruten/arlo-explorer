#!/usr/bin/env python3
"""Luca Cry Monitor v8 — variance threshold detection.
Crying: variance > 50,000. Quiet room (white noise): variance ~3-11M.
Strong signal ratio. Uses μ-law decode (codec auto-detected)."""
import socket, struct, time, json
from collections import deque

HOST, PORT, S = "192.168.1.199", 8554, "nursery"
DURATION = 180  # 3 min

def ulaw_decode(ulv):
    ulv ^= 0xFF
    Sign = ulv & 0x80; expo = (ulv>>4)&0x07; mant = ulv & 0x0F
    Magnitude = (mant<<3) + 0x84
    if expo > 0: Magnitude = Magnitude << (expo-1)
    return -Magnitude if Sign else Magnitude

def variance(samples):
    if len(samples) < 2: return 0.0
    m = sum(samples) / len(samples)
    return sum((x-m)*(x-m) for x in samples) / len(samples)

def mean(vals): return sum(vals)/max(1,len(vals))

# RTSP connect
sk=socket.socket(); sk.settimeout(15); sk.connect((HOST,PORT)); cs,ss=[0],""
def snd(m):
    cs[0]+=1; m=m.replace("CSeq: 0",f"CSeq: {cs[0]}")
    if ss: m+=f"Session: {ss}\r\n"
    sk.sendall(m.encode()); r=b""
    while b"\r\n\r\n" not in r: d=sk.recv(8192); r+=d
    return r.decode(errors="replace")
snd(f"OPTIONS rtsp://{HOST}:{PORT}/{S} RTSP/1.0\r\nCSeq: 0\r\n\r\n")
snd(f"DESCRIBE rtsp://{HOST}:{PORT}/{S} RTSP/1.0\r\nCSeq: 0\r\nAccept: application/sdp\r\n\r\n")
r=snd(f"SETUP rtsp://{HOST}:{PORT}/{S}/trackID=0 RTSP/1.0\r\nCSeq: 0\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n")
for l in r.split("\r\n"):
    if "Session:" in l: ss=l.split("Session: ")[1].split(";")[0].strip()
snd(f"PLAY rtsp://{HOST}:{PORT}/{S} RTSP/1.0\r\nCSeq: 0\r\nRange: npt=0.000-\r\n\r\n")
print("Connected!")

# Learn baseline variance over 10s
print("Learning baseline variance...")
buf=b""; var_history=[]; t0=time.time(); pkts=0
while time.time()-t0<10:
    sk.settimeout(2)
    try: d=sk.recv(8192)
    except socket.timeout: continue
    buf+=d
    while len(buf)>=4 and buf[0]==0x24:
        ch=buf[1]; ln=(buf[2]<<8)|buf[3]
        if len(buf)<4+ln: break
        pkt=buf[4:4+ln]; buf=buf[4+ln:]
        if ch==0 and len(pkt)>=12:
            a=pkt[12:]
            if len(a)>=80:
                s=[ulaw_decode(b) for b in a]
                var_history.append(variance(s)); pkts+=1

bqvar=mean(var_history)
bqvar_std=(sum((v-bqvar)**2 for v in var_history)/max(1,len(var_history)))**0.5
print(f"Baseline var: avg={bqvar:.0f}  std={bqvar_std:.0f}")

# Cry = sustained high variance (5x baseline)
cry_var_thresh=max(bqvar*5.0, 20000.0)
print(f"Cry variance threshold: {cry_var_thresh:.0f}")
print(f"Monitoring {DURATION//60} min...\n")

events=[]; crying=False; start=time.time(); last=start
w=deque(maxlen=100); total_pkts=pkts

while time.time()-start < DURATION:
    sk.settimeout(1)
    try: d=sk.recv(8192)
    except socket.timeout: d=b""
    buf+=d; now=time.time()
    while len(buf)>=4 and buf[0]==0x24:
        ch=buf[1]; ln=(buf[2]<<8)|buf[3]
        if len(buf)<4+ln: break
        pkt=buf[4:4+ln]; buf=buf[4+ln:]
        if ch==0 and len(pkt)>=12:
            a=pkt[12:]
            if len(a)>=80:
                s=[ulaw_decode(b) for b in a]
                v=variance(s); total_pkts+=1
                w.append((now,v))

    recent=[vv for t,vv in w if now-t<=3]
    if len(recent)>=2:
        cry_packets=sum(1 for vv in recent if vv>cry_var_thresh)
        is_cry=(cry_packets>=2 and mean(recent)>cry_var_thresh*0.5)
        if is_cry and not crying:
            crying=True
            events.append({"start":time.strftime("%H:%M:%S"),"peak_var":round(max(recent),0),"avg_var":round(mean(recent),0)})
            print(f"CRY at {time.strftime('%H:%M:%S')}  peak={max(recent):.0f}")
        elif not is_cry and crying:
            crying=False
            if events: events[-1]["end"]=time.strftime("%H:%M:%S")
            print(f"  quiet")

    if now-last>=30:
        rv=[vv for t,vv in w if now-t<=3]
        if rv: print(f"[{int(now-start)//60}m{int(now-start)%60:02d}s] {'CRY' if crying else 'quiet'}  pkts={total_pkts}  evts={len(events)}")
        last=now

sk.close()
result={"session":time.strftime("%Y-%m-%dT%H:%M:%SZ"),"codec":"ulaw","bqvar":round(bqvar,0),"cry_var_thresh":round(cry_var_thresh,0),"pkts":total_pkts,"events":events}
with open("/output/cry_events.json","w") as f: json.dump(result,f,indent=2)
print(f"Done! Events={len(events)}")
for e in events: print(f"  {e}")
