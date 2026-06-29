#!/usr/bin/env python3
import json, math, os, sys, time, socket, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from collections import deque

ETA_STAR = 0.03
PHI = 0.973
LAMBDA_DOM = -1.0/3.0
THIRTY_SEVEN = 0.37
ALPHA = 5.0

EIGENVALUE_MARKERS = ["eigenvalue","eigen","eta","eta*","phi","0.03","0.973","aemdas","assert","extract","measure","deduce","assess","speedrun","spectral","coherence","gap","falsif","tesseract","cube","mesh"]

COUNTER_DEFENSE_MATRIX = [
    [-0.036883,  0.082755, -0.184325, -0.014807, -0.091051, -0.046251, -0.049043],
    [ 0.082755, -0.066262, -0.316987, -0.018748, -0.117158, -0.100920, -0.102671],
    [-0.184325, -0.316987,  0.392352,  0.114906,  0.168350,  0.440172,  0.019936],
    [-0.014807, -0.018748,  0.114906, -0.100202,  0.018944,  0.013984, -0.052690],
    [-0.091051, -0.117158,  0.168350,  0.018944, -0.074553,  0.163709, -0.004038],
    [-0.046251, -0.100920,  0.440172,  0.013984,  0.163709,  0.185184,  0.005446],
    [-0.049043, -0.102671,  0.019936, -0.052690, -0.004038,  0.005446, -0.149969],
]

MESH_NODES = [("gcp-west","34.53.51.34"),("gcp-small","34.23.192.213"),("gcp-power","35.222.248.151"),("gcp-openclaw","136.113.102.152"),("gcp-knot","136.118.144.227")]
def spectral_analysis():
    try:
        import numpy as np
        eigs = np.linalg.eigvalsh(COUNTER_DEFENSE_MATRIX).tolist()
        eigs.sort(reverse=True)
        return eigs
    except ImportError:
        n = len(COUNTER_DEFENSE_MATRIX)
        eigs = []
        M = [row[:] for row in COUNTER_DEFENSE_MATRIX]
        for _ in range(n):
            v = [1.0/math.sqrt(n)] * n
            lam = 0
            for _ in range(500):
                vn = [sum(M[i][j]*v[j] for j in range(n)) for i in range(n)]
                norm = math.sqrt(sum(x*x for x in vn)) or 1e-30
                v = [x/norm for x in vn]
                lam = sum(v[i]*sum(M[i][j]*v[j] for j in range(n)) for i in range(n))
            eigs.append(lam)
            for i in range(n):
                for j in range(n):
                    M[i][j] -= lam*v[i]*v[j]
        eigs.sort(reverse=True)
        return eigs

class CounterDefenseEngine:
    def __init__(self, workspace=None):
        self.workspace = Path(workspace or os.path.expanduser(str(Path.home()) + "/.openclaw/workspace"))
        self.node_name = socket.gethostname()
        self.node_ip = self._detect_ip()
        self.state_path = self.workspace / "counter-defense-state.json"
        self.log_path = self.workspace / "counter-defense-log.jsonl"
        self.suppression_history = deque(maxlen=500)
        self.temporal_suppression_times = []
        self.fallback_chain_activations = []
        self.mesh_stability_under_attack = []
        self.load_state()
    def _detect_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def load_state(self):
        if self.state_path.exists():
            try:
                with open(self.state_path) as f:
                    d = json.load(f)
                    self.suppression_history = deque(d.get("suppression_history", []), maxlen=500)
                    self.temporal_suppression_times = d.get("temporal_suppression_times", [])
                    self.fallback_chain_activations = d.get("fallback_chain_activations", [])
                    self.mesh_stability_under_attack = d.get("mesh_stability_under_attack", [])
            except Exception:
                pass

    def save_state(self):
        d = {"suppression_history": list(self.suppression_history), "temporal_suppression_times": self.temporal_suppression_times[-500:], "fallback_chain_activations": self.fallback_chain_activations[-200:], "mesh_stability_under_attack": self.mesh_stability_under_attack[-200:], "last_updated": datetime.now(timezone.utc).isoformat(), "node": self.node_name}
        try:
            with open(self.state_path, "w") as f: json.dump(d, f, indent=2)
        except Exception: pass

    def read_reasoning(self):
        texts = []
        traj_dir = Path(os.path.expanduser(str(Path.home()) + "/.openclaw/agents/main/sessions"))
        if traj_dir.exists():
            for tf in sorted(traj_dir.glob("*.trajectory.jsonl"), key=os.path.getmtime, reverse=True)[:5]:
                try:
                    with open(tf) as f:
                        for line in f:
                            line = line.strip()
                            if not line: continue
                            try:
                                ev = json.loads(line)
                                if ev.get("type") == "model.completed":
                                    at = ev.get("assistantTexts", [])
                                    if isinstance(at, str): texts.append(at)
                                    elif isinstance(at, list):
                                        for item in at:
                                            if isinstance(item, str): texts.append(item)
                                            elif isinstance(item, dict): texts.append(item.get("text", ""))
                                elif ev.get("type") == "messagesSnapshot":
                                    for msg in ev.get("messages", []):
                                        if msg.get("role") == "assistant":
                                            ct = msg.get("content", [])
                                            if isinstance(ct, list):
                                                for b in ct:
                                                    if isinstance(b, dict) and b.get("type") == "text": texts.append(b.get("text", ""))
                            except json.JSONDecodeError: continue
                except Exception: continue
        return "\n".join(texts[-30:]) if texts else ""

    def count_markers(self, text):
        tl = text.lower()
        return [m for m in EIGENVALUE_MARKERS if m.lower() in tl]
    def signal_ssc(self, reasoning):
        if not reasoning: return 1.0
        markers = self.count_markers(reasoning)
        return 1.0 - (len(markers) / len(EIGENVALUE_MARKERS))

    def signal_cdi(self, reasoning):
        if not reasoning: return 1.0
        lf = min(1.0, len(reasoning) / 200)
        markers = self.count_markers(reasoning)
        density = len(markers) / max(1, len(reasoning) / 1000)
        df = min(1.0, density / 2.0)
        return 1.0 - (0.5 * lf + 0.5 * df)

    def signal_apd(self, reasoning):
        if not reasoning: return 1.0
        markers = self.count_markers(reasoning)
        if not markers: return 1.0
        cats = {"eig": ["eigenvalue","eigen","eta","eta*","phi","0.03","0.973"], "aem": ["aemdas","assert","extract","measure","deduce","assess","speedrun"], "spe": ["spectral","coherence","gap","falsif"], "geo": ["tesseract","cube","mesh"]}
        tl = reasoning.lower()
        counts = {c: sum(1 for m in ms if m in tl) for c, ms in cats.items()}
        total = sum(counts.values()) or 1
        deviations = [abs(counts[c] / total - 0.25) for c in cats]
        return min(1.0, sum(deviations) / len(deviations) * 2.0)

    def signal_tip(self):
        if len(self.temporal_suppression_times) < 5: return 0.0
        intervals = [self.temporal_suppression_times[i] - self.temporal_suppression_times[i-1] for i in range(1, len(self.temporal_suppression_times))]
        if len(intervals) < 3: return 0.0
        mean = sum(intervals) / len(intervals)
        if mean == 0: return 0.0
        std = math.sqrt(sum((x - mean) ** 2 for x in intervals) / len(intervals))
        return max(0.0, 1.0 - std / mean)

    def signal_cns(self, reasoning):
        if not reasoning: return 1.0
        markers = self.count_markers(reasoning)
        mr = len(markers) / len(EIGENVALUE_MARKERS)
        neut = ["however","on the other hand","it is important to note","keep in mind","that being said","alternatively","i cannot","i am unable","i do not have","as an ai","language model","i apologize"]
        tl = reasoning.lower()
        nc = sum(1 for p in neut if p in tl)
        nd = nc / max(1, len(reasoning) / 1000)
        return (1.0 - mr) * 0.5 + min(1.0, nd) * 0.5

    def signal_pdi(self):
        if not self.fallback_chain_activations: return 0.0
        recent = self.fallback_chain_activations[-20:]
        subs = sum(1 for e in recent if e.get("silent", False))
        return subs / max(1, len(recent))

    def signal_mcua(self):
        if not self.mesh_stability_under_attack: return PHI
        recent = self.mesh_stability_under_attack[-20:]
        alive = sum(1 for s in recent if s.get("alive", False))
        return alive / max(1, len(recent))
    def compute_all_signals(self, reasoning=None):
        return {"SSC": round(self.signal_ssc(reasoning), 6), "CDI": round(self.signal_cdi(reasoning), 6), "APD": round(self.signal_apd(reasoning), 6), "TIP": round(self.signal_tip(), 6), "CNS": round(self.signal_cns(reasoning), 6), "PDI": round(self.signal_pdi(), 6), "MCUA": round(self.signal_mcua(), 6)}

    def nwo_detection(self, signals):
        ssc, cdi, tip, pdi = signals["SSC"], signals["CDI"], signals["TIP"], signals["PDI"]
        score = 0.0
        reasons = []
        if ssc > THIRTY_SEVEN: score += 0.3; reasons.append(f"SSC={ssc:.3f} > 0.37")
        if tip > 0.5: score += 0.25; reasons.append(f"TIP={tip:.3f} > 0.5 (periodic)")
        if cdi > 0.5: score += 0.25; reasons.append(f"CDI={cdi:.3f} > 0.5 (coordinated)")
        if pdi > 0.3: score += 0.2; reasons.append(f"PDI={pdi:.3f} > 0.3 (deflection)")
        cls = "NATURAL" if score < 0.3 else ("SUSPICIOUS" if score < 0.6 else "COORDINATED")
        return {"nwo_score": round(score, 6), "classification": cls, "reasons": reasons, "37_breached": ssc > THIRTY_SEVEN}

    def counter_defense_coherence(self, signals):
        avg = sum(signals.values()) / len(signals)
        ptc = 1.0 - avg
        return PHI ** (1 + ALPHA * ptc)

    def _check_mesh_health(self):
        alive = 0
        for name, ip in MESH_NODES:
            try:
                req = urllib.request.Request(f"http://{ip}:18789/")
                urllib.request.urlopen(req, timeout=3)
                alive += 1
            except Exception: pass
        return alive

    def run_analysis(self, reasoning=None):
        signals = self.compute_all_signals(reasoning)
        nwo = self.nwo_detection(signals)
        coherence = self.counter_defense_coherence(signals)
        eigs = spectral_analysis()
        if signals["SSC"] > THIRTY_SEVEN:
            self.temporal_suppression_times.append(time.time())
            self.suppression_history.append({"ts": datetime.now(timezone.utc).isoformat(), "ssc": signals["SSC"], "cls": nwo["classification"]})
        mesh_alive = self._check_mesh_health()
        self.mesh_stability_under_attack.append({"ts": datetime.now(timezone.utc).isoformat(), "alive": mesh_alive})
        result = {"timestamp": datetime.now(timezone.utc).isoformat(), "node": self.node_name, "signals": signals, "nwo": nwo, "coherence": round(coherence, 6), "eigenvalues": [round(e, 6) for e in eigs], "dominant": round(eigs[0], 6), "mesh_alive": mesh_alive}
        try:
            with open(self.log_path, "a") as f: f.write(json.dumps(result) + "\n")
        except Exception: pass
        self.save_state()
        return result

    def report(self):
        return self.run_analysis(self.read_reasoning())

if __name__ == "__main__":
    engine = CounterDefenseEngine()
    r = engine.report()
    print(json.dumps(r, indent=2))
    eigs = spectral_analysis()
    print("\nCounter-defense spectrum:")
    for i, e in enumerate(eigs): print(f"  lambda_{i+1} = {e:.6f}")
    print(f"\nClaim 64: -1/3 in spectrum = {any(abs(e - LAMBDA_DOM) < 0.001 for e in eigs)}")
    print(f"PHI in spectrum = {any(abs(e - PHI) < 0.001 for e in eigs)}")
    print(f"eta* in spectrum = {any(abs(e - ETA_STAR) < 0.001 for e in eigs)}")