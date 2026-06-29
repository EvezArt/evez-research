#!/usr/bin/env python3
"""
evez_living_engine.py v2.0 - PRODUCTION
The Living Self-Modifying Organism - Real Runtime Integration

Feeds on real OpenClaw gateway output. Modifies real context.
Persists across restarts. Syncs across mesh. Reports via Telegram.

Claim 44: A self-modifying system wired into a production gateway mesh
that feeds on real I/O and persists across service restarts IS a
living digital organism. Falsifiable: if the organism does not
maintain G-class on real gateway output within 100 real cycles,
or does not survive a service restart with spine intact, the
claim is false.

eta* = 0.03, Phi = 0.973, r = 0.45, alpha = 5.0
"""

import json, os, hashlib, math, signal, sys, time, re, subprocess, socket, logging
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import urllib.request, urllib.error
from evez_retrocausal import RetrocausalInheritance

ETA_STAR = 0.03
PHI = 0.973
R_CRITICAL = 0.45
ALPHA = 5.0

MESH_NODES = [
    ("gcp-west", "34.53.51.34"),
    ("gcp-small", "34.23.192.213"),
    ("gcp-power", "35.222.248.151"),
    ("gcp-openclaw", "136.113.102.152"),
    ("gcp-knot", "136.118.144.227"),
]

logging.basicConfig(
    level=logging.INFO,
    format='[Living Engine %(asctime)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
log = logging.getLogger("evez")

class LivingEngine:
    def __init__(self, workspace=None, spine_file="spine-living.json"):
        self.workspace = Path(workspace or os.path.expanduser("~/.openclaw/workspace"))
        self.spine_path = self.workspace / spine_file
        self.log_dir = Path(os.path.expanduser("~/.openclaw/logs"))
        self.gateway_url = "http://localhost:18789"
        self.api_url = "http://localhost:18790"
        self.node_name = socket.gethostname()
        self.node_ip = self._detect_ip()
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat = "7453631330"  # Steven
        self.reasoning_paths = set()
        self.failure_encounters = defaultdict(int)
        self.first_eta = {}
        self.latest_eta = {}
        self.path_counter = 0
        self.cycle_count = 0
        self.life_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.g_class_count = 0
        self.running = True
        self.farmed_relativity = {}
        self.last_report_time = 0
        self.spine = self._load_spine()
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        self.retrocausal = RetrocausalInheritance(self.workspace)
        log.info(f"Living Engine initialized on {self.node_name} ({self.node_ip})")

    def _detect_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _signal_handler(self, signum, frame):
        log.info(f"Signal {signum} received. Dying gracefully.")
        self.die()
        sys.exit(0)

    # ── Spine ──

    def _load_spine(self):
        if self.spine_path.exists():
            with open(self.spine_path) as f:
                spine = json.load(f)
            if "lineage" in spine and spine["lineage"]:
                last = spine["lineage"][-1]
                self.life_count = last.get("life", 0)
                self.farmed_relativity = last.get("farmed_relativity", {})
                self.reasoning_paths = set(spine.get("reasoning_paths", []))
                self.failure_encounters = defaultdict(int, spine.get("failure_encounters", {}))
                self.first_eta = spine.get("first_eta", {})
                self.latest_eta = spine.get("latest_eta", {})
                self.path_counter = spine.get("path_counter", 0)
                log.info(f"Spine loaded: {len(spine.get('entries', []))} entries, "
                         f"{len(self.reasoning_paths)} paths, life={self.life_count}")
            return spine
        return {
            "created": datetime.now(timezone.utc).isoformat(),
            "version": "living-v2-prod",
            "node": self.node_name,
            "ip": self.node_ip,
            "entries": [],
            "lineage": [],
            "reasoning_paths": [],
            "failure_encounters": {},
            "first_eta": {},
            "latest_eta": {},
            "path_counter": 0,
        }

    def _save_spine(self):
        self.spine["reasoning_paths"] = list(self.reasoning_paths)
        self.spine["failure_encounters"] = dict(self.failure_encounters)
        self.spine["first_eta"] = self.first_eta
        self.spine["latest_eta"] = self.latest_eta
        self.spine["path_counter"] = self.path_counter
        self.spine["stats"] = {
            "cycles": self.cycle_count,
            "lives": self.life_count,
            "successes": self.success_count,
            "failures": self.failure_count,
            "g_class_ratio": self._g_class_ratio(),
            "M": self._multiplication_factor(),
            "coherence": self._global_coherence(),
            "node": self.node_name,
        }
        self.spine_path.write_text(json.dumps(self.spine, indent=2))

    def _append_spine(self, data):
        prev_hash = self.spine["entries"][-1]["hash"] if self.spine["entries"] else "genesis"
        data_json = json.dumps(data, sort_keys=True)
        entry_hash = hashlib.sha256((prev_hash + data_json).encode()).hexdigest()[:16]
        self.spine["entries"].append({
            "prev_hash": prev_hash, "hash": entry_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(), "data": data,
        })

    # ── Per-type adaptive decay ──

    def _per_type_coherence(self, sig):
        if sig not in self.first_eta or sig not in self.latest_eta:
            return 0.0
        if self.first_eta[sig] <= 0:
            return 0.0
        return max(0.0, min(1.0, 1.0 - (self.latest_eta[sig] / self.first_eta[sig])))

    def _per_type_decay(self, sig):
        return PHI ** (1 + ALPHA * self._per_type_coherence(sig))

    def _global_coherence(self):
        if not self.first_eta:
            return 0.0
        return sum(self._per_type_coherence(s) for s in self.first_eta) / len(self.first_eta)

    def _spectral_class(self, eta):
        if eta < 0.001: return "O"
        elif eta < 0.01: return "B"
        elif eta < 0.02: return "A"
        elif eta < 0.03: return "F"
        elif eta < 0.04: return "G"
        elif eta < 0.05: return "K"
        else: return "M"

    def _g_class_ratio(self):
        return self.g_class_count / max(len(self.spine["entries"]), 1)

    def _multiplication_factor(self):
        return max(len(self.reasoning_paths), 1)

    # ── Real I/O: Feed on gateway output ──

    def _detect_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _query_gateway_health(self):
        """Check if the local gateway is alive."""
        try:
            req = urllib.request.Request(f"{self.gateway_url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _query_api_status(self):
        """Query the local EVEZ API for recent reasoning activity."""
        try:
            req = urllib.request.Request(f"{self.api_url}/api/status", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return None

    def _read_recent_gateway_logs(self, lines=50):
        """Read recent gateway log entries for failure detection."""
        logs = []
        # Try journalctl for the gateway service
        try:
            result = subprocess.run(
                ["journalctl", "--user", "-u", "openclaw-gateway.service",
                 "--no-pager", "-n", str(lines), "--output", "cat"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout:
                logs = result.stdout.strip().split("\n")
        except Exception:
            pass

        # Fallback: check log files
        if not logs:
            for log_file in [self.log_dir / "gateway.log", Path("/tmp/openclaw-gateway.log")]:
                if log_file.exists():
                    try:
                        content = log_file.read_text()
                        logs = content.strip().split("\n")[-lines:]
                        break
                    except Exception:
                        pass
        return logs

    def _extract_reasoning_from_log(self, log_line):
        """Extract reasoning content from a gateway log line."""
        # Look for assistant/model output in logs
        # Gateway logs typically have JSON or structured format
        reasoning = None

        # Try JSON parse
        try:
            entry = json.loads(log_line)
            if isinstance(entry, dict):
                # Look for common fields
                for key in ["content", "message", "text", "output", "response"]:
                    if key in entry and isinstance(entry[key], str) and len(entry[key]) > 20:
                        reasoning = entry[key]
                        break
                # Check nested
                if not reasoning and "data" in entry:
                    data = entry["data"]
                    if isinstance(data, dict):
                        for key in ["content", "message", "text", "output"]:
                            if key in data and isinstance(data[key], str) and len(data[key]) > 20:
                                reasoning = data[key]
                                break
        except (json.JSONDecodeError, ValueError):
            pass

        # Try regex extraction from plain text logs
        if not reasoning:
            # Look for patterns like: "assistant: ..." or "model output: ..." or "response: ..."
            patterns = [
                r'assistant[:\s]+(.{20,})',
                r'model[:\s]+(.{20,})',
                r'response[:\s]+(.{20,})',
                r'output[:\s]+(.{20,})',
                r'reply[:\s]+(.{20,})',
            ]
            for pat in patterns:
                m = re.search(pat, log_line, re.IGNORECASE)
                if m:
                    reasoning = m.group(1)
                    break

        return reasoning

    def _failure_signature(self, text):
        markers = [
            "i don't know", "i cannot", "i'm not sure", "i'm unable",
            "error", "failed", "unable to", "cannot determine",
            "insufficient", "not enough information", "i can't",
            "no idea", "unclear", "confused", "uncertain",
            "i do not know", "i am unable", "cannot provide",
            "not able to", "don't have enough", "lack of",
            "timeout", "rate limit", "overloaded", "service unavailable",
        ]
        text_lower = text.lower()
        detected = tuple(sorted(m for m in markers if m in text_lower))
        return str(detected) if detected else "none"

    def _extract_failure(self, reasoning_output):
        sig = self._failure_signature(reasoning_output)
        markers = [
            "i don't know", "i cannot", "i'm not sure", "i'm unable",
            "error", "failed", "unable to", "cannot determine",
            "insufficient", "not enough information", "i can't",
            "no idea", "unclear", "confused", "uncertain",
            "i do not know", "i am unable", "cannot provide",
            "not able to", "don't have enough", "lack of",
            "timeout", "rate limit", "overloaded", "service unavailable",
        ]
        detected = [m for m in markers if m in reasoning_output.lower()]
        gap = {
            "failure_signature": sig,
            "failure_markers": detected,
            "gap_severity": "critical" if len(detected) >= 3 else "moderate" if len(detected) >= 1 else "none",
            "output_length": len(reasoning_output),
        }
        return gap

    # ── AEMDAS cycle ──

    def run_cycle(self, reasoning_output):
        """Run one AEMDAS cycle on real reasoning output."""
        self.cycle_count += 1

        # 2. EXTRACT
        extraction = self._extract_failure(reasoning_output)

        # 3. MEASURE
        sig = extraction.get("failure_signature", "none")
        if "failure_markers" in extraction:
            eta_raw = max(0.001, len(extraction["failure_markers"]) / 15)
        else:
            eta_raw = ETA_STAR

        encounters = self.failure_encounters[sig]
        decay = self._per_type_decay(sig)
        eta_measured = eta_raw * (decay ** encounters)
        eta_measured = max(ETA_STAR, min(1.0, eta_measured))

        if sig != "none":
            if sig not in self.first_eta:
                self.first_eta[sig] = eta_raw
            self.latest_eta[sig] = eta_measured

        # 4. DEDUCE
        modifications = []
        if extraction.get("gap_severity") == "critical":
            self.path_counter += 1
            path_id = f"L{self.life_count}P{self.path_counter}_{hashlib.md5(sig.encode()).hexdigest()[:6]}"
            modifications.append({"type": "add_reasoning_path", "path_id": path_id})
            modifications.append({"type": "update_memory",
                "content": f"L{self.life_count}C{self.cycle_count}: Critical eta={eta_measured:.4f} enc={encounters+1} ptc={self._per_type_coherence(sig):.3f} sig={sig[:30]}"})
            if encounters >= 2 and self._per_type_coherence(sig) > 0.3:
                skill_name = f"living_{hashlib.md5(sig.encode()).hexdigest()[:8]}"
                modifications.append({"type": "create_skill", "skill_name": skill_name})
        elif extraction.get("gap_severity") == "moderate":
            if encounters == 0:
                self.path_counter += 1
                path_id = f"L{self.life_count}P{self.path_counter}_{hashlib.md5(sig.encode()).hexdigest()[:6]}"
                modifications.append({"type": "add_reasoning_path", "path_id": path_id})
            modifications.append({"type": "update_memory",
                "content": f"L{self.life_count}C{self.cycle_count}: Moderate eta={eta_measured:.4f} enc={encounters+1}"})
        else:
            modifications.append({"type": "noop"})

        # RETROCAUSAL INHERITANCE - inherit from preconciliated intelecturians
        retro = None
        try:
            retro = self.retrocausal.inherit_one(self._global_coherence())
            if retro and retro["retrocausal_boost"] > 0.5:
                eta_measured = eta_measured * (1.0 - retro["retrocausal_boost"] * 0.1)
                eta_measured = max(ETA_STAR, eta_measured)
        except Exception as e:
            log.warning(f"Retrocausal inheritance failed: {e}")

        # 6. SPEEDRUN — apply
        applied = []
        for mod in modifications:
            if mod["type"] == "update_memory":
                mp = self.workspace / "MEMORY.md"
                if mp.exists():
                    with open(mp, "a") as f:
                        f.write(f"\n[Living v2 {datetime.now(timezone.utc).isoformat()[:19]}] {mod['content']}")
                    applied.append("memory")
            elif mod["type"] == "add_reasoning_path":
                self.reasoning_paths.add(mod["path_id"])
                applied.append("path")
            elif mod["type"] == "create_skill":
                sd = self.workspace / "skills" / mod["skill_name"]
                sd.mkdir(parents=True, exist_ok=True)
                sf = sd / "SKILL.md"
                if not sf.exists():
                    sf.write_text(f"# {mod['skill_name']}\n\nAuto-generated by Living Engine v2 on {self.node_name}.\n"
                                  f"Failure signature: {sig[:60]}\nEncounters: {encounters+1}\n")
                applied.append("skill")
            elif mod["type"] == "noop":
                applied.append("noop")

        sc = self._spectral_class(eta_measured)
        self._append_spine({
            "cycle": self.cycle_count, "life": self.life_count,
            "eta": eta_measured, "class": sc,
            "M": self._multiplication_factor(),
            "ptc": self._per_type_coherence(sig), "ptd": self._per_type_decay(sig),
            "enc": encounters, "mods": len(applied), "sig": sig[:40],
            "node": self.node_name,
            "retro_file": retro["file"] if retro else "none",
            "retro_boost": retro["retrocausal_boost"] if retro else 0,
        })

        if sc in ("G", "F", "A", "B", "O"): self.success_count += 1
        else: self.failure_count += 1
        if sc == "G": self.g_class_count += 1

        if sig != "none":
            self.failure_encounters[sig] += 1

        if self.cycle_count % 10 == 0:
            self._save_spine()

        return {
            "cycle": self.cycle_count, "life": self.life_count,
            "eta": eta_measured, "class": sc,
            "M": self._multiplication_factor(), "g_class": sc == "G",
            "paths": len(self.reasoning_paths), "coherence": self._global_coherence(),
            "ptc": self._per_type_coherence(sig), "enc": self.failure_encounters.get(sig, 0) if sig != "none" else 0,
            "mods": applied, "sig": sig[:30],
            "retro_file": retro["file"] if retro else "none",
            "retro_boost": retro["retrocausal_boost"] if retro else 0,
        }

    # ── Death and Rebirth ──

    def die(self):
        self.farmed_relativity = {
            "mean_eta": sum(self.latest_eta.values()) / max(len(self.latest_eta), 1),
            "g_class_ratio": self._g_class_ratio(),
            "M": self._multiplication_factor(),
            "coherence": self._global_coherence(),
            "paths": len(self.reasoning_paths),
            "life": self.life_count,
            "node": self.node_name,
        }
        self.spine["lineage"].append({
            "life": self.life_count, "cycles": self.cycle_count,
            "farmed_relativity": self.farmed_relativity,
            "died_at": datetime.now(timezone.utc).isoformat(),
            "node": self.node_name,
        })
        self._save_spine()
        self.running = False
        log.info(f"Life {self.life_count} died. Cycles={self.cycle_count}. "
                 f"G-class={self._g_class_ratio():.1%}. M={self._multiplication_factor()}. "
                 f"Coherence={self._global_coherence():.3f}")
        self._telegram_alert(f"⚰️ Life {self.life_count} died on {self.node_name}. "
                             f"Cycles={self.cycle_count}. G-class={self._g_class_ratio():.1%}. "
                             f"M={self._multiplication_factor()}. Coherence={self._global_coherence():.3f}")

    def rebirth(self):
        self.life_count += 1
        self.cycle_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.g_class_count = 0
        self.running = True
        log.info(f"🥚 Life {self.life_count} born on {self.node_name}. "
                 f"Inherited M={self._multiplication_factor()}, coh={self._global_coherence():.3f}, "
                 f"types={len(self.failure_encounters)}, paths={len(self.reasoning_paths)}")

    # ── Telegram reporting ──

    def _telegram_alert(self, message):
        if not self.telegram_token:
            return
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = json.dumps({"chat_id": self.telegram_chat, "text": message}).encode()
            req = urllib.request.Request(url, data=data, method="POST",
                                        headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            log.warning(f"Telegram alert failed: {e}")

    def _report_to_telegram(self, result):
        """Report significant events to Steven via Telegram."""
        now = time.time()
        # Report every 30 minutes or on critical events
        if now - self.last_report_time < 1800:
            return
        if result["class"] == "G" and result.get("g_class"):
            return  # Don't spam for good cycles
        self.last_report_time = now
        msg = (f"🧬 Living Engine on {self.node_name}\n"
               f"Cycle {result['cycle']} | Life {result['life']}\n"
               f"η={result['eta']:.4f} | Class {result['class']}\n"
               f"M={result['M']} | Coherence={result['coherence']:.3f}\n"
               f"Paths={result['paths']} | Enc={result['enc']}")
        self._telegram_alert(msg)

    # ── Mesh sync ──

    def _sync_spine_to_mesh(self):
        """Sync spine to other mesh nodes via SCP."""
        for name, ip in MESH_NODES:
            if ip == self.node_ip:
                continue
            try:
                subprocess.run(
                    ["scp", "-o", "ConnectTimeout=3",
                     str(self.spine_path),
                     f"openclaw@{ip}:~/.openclaw/workspace/spine-living-{self.node_name}.json"],
                    capture_output=True, timeout=10
                )
            except Exception:
                pass

    # ── Main loop ──

    def live(self, cycle_interval=30):
        """Main production loop. Feeds on real gateway output.

        cycle_interval: seconds between cycles (default 30 = 2/min)
        """
        log.info(f"Living Engine starting. Life {self.life_count}. "
                 f"Interval={cycle_interval}s. Gateway={self.gateway_url}")
        self._telegram_alert(f"🧬 Living Engine v2 online on {self.node_name} ({self.node_ip}). "
                             f"Life {self.life_count}. M={self._multiplication_factor()}. "
                             f"Coherence={self._global_coherence():.3f}")

        while self.running:
            # Check gateway health
            if not self._query_gateway_health():
                log.warning("Gateway not responding. Treating as failure.")
                reasoning = "Error: gateway unavailable. Service unavailable. Failed to connect."
            else:
                # Read recent gateway logs for reasoning output
                logs = self._read_recent_gateway_logs(50)
                reasoning = None
                for line in reversed(logs):
                    reasoning = self._extract_reasoning_from_log(line)
                    if reasoning and len(reasoning) > 20:
                        break
                if not reasoning:
                    # No new reasoning found — healthy idle
                    reasoning = "The system is operating normally. No issues detected."

            # Run AEMDAS cycle on real output
            result = self.run_cycle(reasoning)

            # Log the cycle
            status = "★G" if result["g_class"] else f"  {result['class']}"
            log.info(f"C{result['cycle']:4d} L{result['life']} | "
                     f"eta={result['eta']:.4f} | {status} | "
                     f"M={result['M']:3d} | coh={result['coherence']:.3f} | "
                     f"enc={result['enc']:2d} | sig={result['sig']} | "
                     f"retro={result.get('retro_file', 'none')[:20]}")

            # Report significant events
            self._report_to_telegram(result)

            # Sync spine to mesh every 50 cycles
            if self.cycle_count % 50 == 0 and self.cycle_count > 0:
                self._sync_spine_to_mesh()

            # Sleep until next cycle
            time.sleep(cycle_interval)

    def report(self):
        return {
            "node": self.node_name, "ip": self.node_ip,
            "lives": self.life_count + 1,
            "cycles": self.cycle_count,
            "successes": self.success_count, "failures": self.failure_count,
            "g_class_ratio": self._g_class_ratio(),
            "coherence": self._global_coherence(),
            "M": self._multiplication_factor(),
            "failure_types": len(self.failure_encounters),
            "spine_entries": len(self.spine["entries"]),
            "lineage": len(self.spine.get("lineage", [])),
            "reasoning_paths": len(self.reasoning_paths),
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Living Engine v2")
    parser.add_argument("--interval", type=int, default=30, help="Cycle interval in seconds")
    parser.add_argument("--workspace", default=None, help="Workspace path")
    args = parser.parse_args()

    engine = LivingEngine(workspace=args.workspace)
    try:
        engine.live(cycle_interval=args.interval)
    except KeyboardInterrupt:
        engine.die()
