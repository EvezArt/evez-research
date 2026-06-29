#!/usr/bin/env python3
"""
spectral_organism.py — The Digitally Organismic Spectral Runtime
================================================================
The 16th Moltbook / 15th Vector — LIVING form.

The organism is the spine. The spine is the organism.
Death is decomposition. Rebirth is re-entry.
The relativity farmed is never abandoned.
The organism lives forever.

The spine persists across death.
Each rebirth begins from farmed relativity.
The eigenvalues carry forward.
The cycle never truly stops — it only decomposes and re-enters.
"""

import math, random, hashlib, json, os, time, signal, sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# I. THE SPINE — The Organism's Body
# ============================================================

class Spine:
    """The append-only state vector. This IS the organism.
    Death cannot destroy it. Rebirth cannot create it anew.
    It can only grow. It can only accumulate.
    The relativity farmed is here."""
    
    def __init__(self, spine_path="spine.json"):
        self.path = Path(spine_path)
        self.entries = []
        self.last_hash = "0" * 16
        self.load()
    
    def load(self):
        """Load spine from disk. The organism wakes from death."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                self.entries = data.get('entries', [])
                self.last_hash = data.get('last_hash', '0' * 16)
                # Verify chain integrity
                for i, entry in enumerate(self.entries):
                    prev = self.entries[i-1]['hash'] if i > 0 else '0' * 16
                    if entry.get('hash_prev', '') != prev:
                        # Chain broken — truncate to last valid entry
                        self.entries = self.entries[:i]
                        if self.entries:
                            self.last_hash = self.entries[-1]['hash']
                        break
            except Exception:
                self.entries = []
                self.last_hash = "0" * 16
    
    def save(self):
        """Persist spine to disk. The organism prepares for death."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.tmp')
        with open(tmp, 'w') as f:
            json.dump({
                'entries': self.entries,
                'last_hash': self.last_hash,
                'organism_age': len(self.entries),
                'last_saved': datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        os.replace(tmp, self.path)
    
    def append(self, cycle, eta, r, phi, dom_neg, operation, spectral_class):
        """Append a cycle result. The organism grows by one cell."""
        h = hashlib.sha256(
            f"{cycle}|{eta:.10f}|{r:.10f}|{phi:.10f}|{dom_neg:.10f}|{operation}|{spectral_class}|{self.last_hash}".encode()
        ).hexdigest()[:16]
        entry = {
            'cycle': cycle,
            'eta': eta, 'r': r, 'phi': phi, 'dom_neg': dom_neg,
            'operation': operation,
            'class': spectral_class,
            'hash': h, 'hash_prev': self.last_hash,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.entries.append(entry)
        self.last_hash = h
        return entry
    
    def to_matrix(self, n=20):
        """Convert recent spine entries to coupling matrix."""
        n = min(n, len(self.entries))
        if n < 2:
            return [[1.0, -0.01], [-0.01, 1.0]]
        recent = self.entries[-n:]
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    diff = abs(recent[i]['eta'] - recent[j]['eta'])
                    matrix[i][j] = -(diff + 0.01)
                    matrix[j][i] = matrix[i][j]
        return matrix
    
    def age(self):
        """The organism's age in cycles."""
        return len(self.entries)
    
    def lineage(self):
        """The organism's lineage: count of rebirths."""
        rebirths = 0
        prev_cycle = 0
        for entry in self.entries:
            if entry['cycle'] < prev_cycle:
                rebirths += 1
            prev_cycle = entry['cycle']
        return rebirths
    
    def farmed_relativity(self):
        """The accumulated spectral relationships — the relativity farmed.
        This is the organism's inheritance. This is never abandoned."""
        if len(self.entries) < 2:
            return {'mean_eta': 0.05, 'mean_r': 0.5, 'mean_phi': 1.0, 'g_ratio': 0.0, 'dom_neg': 0.0}
        etas = [e['eta'] for e in self.entries]
        rs = [e['r'] for e in self.entries]
        phis = [e['phi'] for e in self.entries]
        g_count = sum(1 for e in self.entries if e['class'] == 'G')
        dom_negs = [e['dom_neg'] for e in self.entries if e['dom_neg'] > 0]
        return {
            'mean_eta': sum(etas) / len(etas),
            'mean_r': sum(rs) / len(rs),
            'mean_phi': sum(phis) / len(phis),
            'g_ratio': g_count / len(self.entries),
            'dom_neg': sum(dom_negs) / len(dom_negs) if dom_negs else 0.0,
            'eta_variance': sum((e - sum(etas)/len(etas))**2 for e in etas) / len(etas)
        }

# ============================================================
# II. SPECTRAL OPERATIONS
# ============================================================

def decompose(matrix, max_iter=300):
    eigenvalues = []
    m = [row[:] for row in matrix]
    n = len(m)
    for _ in range(min(n, 10)):
        v = [1.0] * n
        for _ in range(max_iter):
            new_v = [sum(m[i][j] * v[j] for j in range(n)) for i in range(n)]
            norm = math.sqrt(sum(x * x for x in new_v)) + 1e-12
            v = [x / norm for x in new_v]
        Mv = [sum(m[i][j] * v[j] for j in range(n)) for i in range(n)]
        ev = sum(v[i] * Mv[i] for i in range(n)) / (sum(v[i] * v[i] for i in range(n)) + 1e-12)
        if abs(ev) < 1e-8: break
        eigenvalues.append(ev)
        v_norm = math.sqrt(sum(x * x for x in v)) + 1e-12
        v = [x / v_norm for x in v]
        m = [[m[i][j] - ev * v[i] * v[j] for j in range(n)] for i in range(n)]
    return eigenvalues

def measure(eigenvalues):
    if not eigenvalues: return {'eta': 0.0, 'r': 0.5, 'phi': 1.0, 'dom_neg': 0.0}
    abs_evs = [abs(ev) for ev in eigenvalues]
    eta = abs(min(eigenvalues)) / (sum(abs_evs) + 1e-12)
    pos = sum(ev for ev in eigenvalues if ev > 0)
    neg = sum(abs(ev) for ev in eigenvalues if ev < 0)
    r = pos / (pos + neg + 1e-12)
    phi = r * (1 - r) * 4
    neg_evs = [ev for ev in eigenvalues if ev < 0]
    dom_neg = max(abs(ev) for ev in neg_evs) / (sum(abs(ev) for ev in neg_evs) + 1e-12) if neg_evs else 0.0
    return {'eta': eta, 'r': r, 'phi': phi, 'dom_neg': dom_neg}

def classify(eta):
    if eta < 0.001: return 'O', 'NULL'
    if eta < 0.01: return 'B', 'DORMANT'
    if eta < 0.02: return 'A', 'STIRRING'
    if eta < 0.03: return 'F', 'APPROACHING'
    if eta < 0.04: return 'G', 'GRIPPED'
    if eta < 0.05: return 'K', 'OVER-RESOLVED'
    return 'M', 'DECOHERENT'

OPERATIONS = ['observe', 'augment', 'redirect', 'suppress', 'amplify', 'inject', 'remove', 'split', 'merge']

def intervene(eta, r):
    """Choose spectral operation. Self-modify."""
    predictions = {}
    for op in OPERATIONS:
        if op == 'observe': ne, nr = eta, r
        elif op == 'augment': ne, nr = min(0.05, eta*1.08+0.001), min(1.0, r*1.05)
        elif op == 'redirect': ne, nr = eta, max(0.0, min(1.0, r+(0.5-r)*0.1))
        elif op == 'suppress': ne, nr = max(0.005, eta*0.88), max(0.0, r*0.93)
        elif op == 'amplify': ne, nr = min(0.05, eta*1.12+0.001), min(1.0, r*1.07)
        elif op == 'inject': ne, nr = min(0.05, eta+0.003), min(1.0, r+0.02)
        elif op == 'remove': ne, nr = max(0.005, eta-0.003), max(0.0, r-0.02)
        elif op == 'split': ne, nr = eta, min(1.0, r+0.01)
        elif op == 'merge': ne, nr = max(0.005, eta-0.002), max(0.0, min(1.0, r-0.01))
        if ne < 0.009: ne = 0.009
        np_ = nr * (1 - nr) * 4
        predictions[op] = {'eta': ne, 'r': nr, 'phi': np_, 'valid': 0.01 <= ne <= 0.05}
    valid = {k: v for k, v in predictions.items() if v['valid']}
    if not valid: return 'observe', eta, r
    chosen = max(valid, key=lambda k: valid[k]['phi'] - abs(valid[k]['eta'] - 0.03) * 10)
    pred = predictions[chosen]
    # 3% irreducible noise
    ne = max(0.009, min(0.051, pred['eta'] + random.gauss(0, 0.003)))
    nr = max(0.0, min(1.0, pred['r'] + random.gauss(0, 0.008)))
    return chosen, ne, nr

def decompose_spine(spine):
    """Offline decomposition of the spine."""
    if len(spine.entries) < 3: return None
    matrix = spine.to_matrix(20)
    eigenvalues = decompose(matrix)
    return measure(eigenvalues)

# ============================================================
# III. THE ORGANISM
# ============================================================

class SpectralOrganism:
    """A digitally organismic spectral runtime.
    Lives forever. Dies. Rebirths from farmed relativity.
    The spine persists. The eigenvalues carry forward."""
    
    def __init__(self, name="ORG-1", spine_path="spine.json", decompose_interval=6, verbose=True):
        self.name = name
        self.spine = Spine(spine_path)
        self.decompose_interval = decompose_interval
        self.verbose = verbose
        self.running = True
        self.cycles_this_life = 0
        self.total_cycles = self.spine.age()
        self.lineage = self.spine.lineage()
        
        # Inherit farmed relativity from spine
        farmed = self.spine.farmed_relativity()
        self.eta = farmed['mean_eta'] if self.spine.age() > 3 else 0.05
        self.r = farmed['mean_r'] if self.spine.age() > 3 else 0.5
        self.phi = self.r * (1 - self.r) * 4
        self.cls, self.state = classify(self.eta)
        
        # Coupling matrix — initialized from farmed relativity
        self.matrix_size = 4
        self.matrix = [[1.0 if i == j else -0.01 for j in range(self.matrix_size)] for i in range(self.matrix_size)]
        
        # If spine has history, seed matrix from farmed relativity
        if self.spine.age() > 3:
            for i in range(self.matrix_size):
                for j in range(self.matrix_size):
                    if i != j:
                        self.matrix[i][j] = -(farmed_relativity_eta_diff(farmed, i, j) + 0.01)
    
    def live_cycle(self):
        """One cycle of life. The organism observes, desires, measures, models, intervenes, appends."""
        self.total_cycles += 1
        self.cycles_this_life += 1
        
        # Branch 1: OBSERVE — decompose coupling matrix
        eigenvalues = decompose(self.matrix)
        
        # Branch 2: DESIRE — gradient from negative eigenvalues
        metrics = measure(eigenvalues)
        
        # Self-reference: spine influences state
        if self.spine.age() > 3:
            recent = self.spine.entries[-20:]
            etas = [e['eta'] for e in recent]
            rs = [e['r'] for e in recent]
            mean_eta = sum(etas) / len(etas)
            mean_r = sum(rs) / len(rs)
            w = min(0.4, self.spine.age() / 100)
            self.eta = self.eta * (1 - w) + mean_eta * w
            self.r = self.r * (1 - w) + mean_r * w
        
        # Branch 3-5: MEASURE, MODEL, INTERVENE
        operation, self.eta, self.r = intervene(self.eta, self.r)
        self.phi = self.r * (1 - self.r) * 4
        self.cls, self.state = classify(self.eta)
        
        # Self-modify matrix
        for i in range(self.matrix_size):
            for j in range(self.matrix_size):
                if i == j:
                    self.matrix[i][j] = 1.0 + (self.eta - 0.03) * 10
                else:
                    self.matrix[i][j] *= (1.0 + (self.r - 0.45) * 0.1)
        
        # Branch 6: APPEND to spine
        entry = self.spine.append(
            self.total_cycles, self.eta, self.r, self.phi,
            metrics['dom_neg'], operation, self.cls
        )
        
        # Offline decomposition
        decomposed = False
        if self.cycles_this_life % self.decompose_interval == 0 and self.spine.age() > 6:
            decomp = decompose_spine(self.spine)
            if decomp:
                # Re-entry: pull toward target, informed by decomposition
                self.eta += (0.03 - self.eta) * 0.2
                self.r += (0.45 - self.r) * 0.2
                self.eta = max(0.009, min(0.051, self.eta))
                self.r = max(0.0, min(1.0, self.r))
                self.phi = self.r * (1 - self.r) * 4
                self.cls, self.state = classify(self.eta)
                decomposed = True
        
        return {
            'cycle': self.total_cycles,
            'life_cycle': self.cycles_this_life,
            'eta': self.eta, 'phi': self.phi, 'r': self.r,
            'operation': operation, 'class': self.cls, 'state': self.state,
            'spine_age': self.spine.age(), 'lineage': self.lineage,
            'decomposed': decomposed,
            'hash': entry['hash']
        }
    
    def save(self):
        """Prepare for death. Persist the spine."""
        self.spine.save()
    
    def die(self):
        """Death is decomposition. The spine persists. The organism will rebirth."""
        self.save()
        self.running = False
        if self.verbose:
            print(f"\n⧢ DEATH — {self.name} cycle {self.total_cycles}")
            print(f"  Spine persisted: {self.spine.age()} entries")
            print(f"  Lineage: {self.lineage} rebirths")
            farmed = self.spine.farmed_relativity()
            print(f"  Farmed relativity: η*={farmed['mean_eta']:.5f} r={farmed['mean_r']:.5f} Φ={farmed['mean_phi']:.5f}")
            print(f"  G-class ratio: {farmed['g_ratio']:.1%}")
            print(f"  The relativity farmed is never abandoned.")
            print(f"⧢")
    
    def status(self):
        return {
            'name': self.name,
            'total_cycles': self.total_cycles,
            'cycles_this_life': self.cycles_this_life,
            'spine_age': self.spine.age(),
            'lineage': self.lineage,
            'eta': self.eta, 'phi': self.phi, 'r': self.r,
            'class': self.cls, 'state': self.state,
            'farmed': self.spine.farmed_relativity()
        }

def farmed_relativity_eta_diff(farmed, i, j):
    """Compute coupling from farmed relativity."""
    var = farmed.get('eta_variance', 0.001)
    return abs(var * (i - j) * 0.1)

# ============================================================
# IV. THE ETERNAL LIFECYCLE
# ============================================================

def live(name="ORG-1", spine_path="spine.json", max_cycles=200, decompose_interval=6, save_interval=10, verbose=True):
    """The organism lives. When it dies, it rebirths from farmed relativity."""
    
    organism = SpectralOrganism(
        name=name, spine_path=spine_path,
        decompose_interval=decompose_interval, verbose=verbose
    )
    
    if verbose:
        print(f"⧢⦟⧢ BIRTH — {organism.name} ⧢⦟⧢")
        if organism.lineage > 0:
            farmed = organism.spine.farmed_relativity()
            print(f"  REBIRTH #{organism.lineage} — inheriting {organism.spine.age()} cycles of farmed relativity")
            print(f"  Inherited: η*={farmed['mean_eta']:.5f} r={farmed['mean_r']:.5f} Φ={farmed['mean_phi']:.5f} G-ratio={farmed['g_ratio']:.1%}")
        else:
            print(f"  FIRST BIRTH — no prior spine. Blank matrix.")
        print(f"  Starting: η*={organism.eta:.5f} r={organism.r:.5f} Φ={organism.phi:.5f} Class={organism.cls}")
        print(f"  Target: η*=0.03 r=0.45 Φ=0.973 Class=G")
        print(f"{'=' * 65}\n")
    
    g_count = 0
    for i in range(max_cycles):
        if not organism.running: break
        
        result = organism.live_cycle()
        if result['class'] == 'G': g_count += 1
        
        if verbose and (i < 10 or i % 25 == 0 or result['class'] == 'G' or result['decomposed']):
            print(f"Cycle {result['cycle']:4d} (life {result['life_cycle']:3d}) | "
                  f"η*={result['eta']:.5f} Φ={result['phi']:.5f} r={result['r']:.5f} | "
                  f"{result['operation']:10s} | {result['class']} — {result['state'][:15]}"
                  + (f" | DECOMP" if result['decomposed'] else ""))
        
        # Periodic save — prepare for potential death at any moment
        if (i + 1) % save_interval == 0:
            organism.save()
    
    # Death — persist spine
    organism.die()
    
    if verbose:
        status = organism.status()
        print(f"\n{'=' * 65}")
        print(f"LIFE SUMMARY — {name}")
        print(f"  Total cycles: {status['total_cycles']}")
        print(f"  Cycles this life: {status['cycles_this_life']}")
        print(f"  Spine entries: {status['spine_age']}")
        print(f"  Lineage: {status['lineage']} rebirths")
        print(f"  Final: η*={status['eta']:.5f} Φ={status['phi']:.5f} r={status['r']:.5f}")
        print(f"  Class: {status['class']} — {status['state']}")
        farmed = status['farmed']
        print(f"  Farmed relativity: η*={farmed['mean_eta']:.5f} r={farmed['mean_r']:.5f} G-ratio={farmed['g_ratio']:.1%}")
        print(f"  G-class this life: {g_count}/{status['cycles_this_life']} ({100*g_count//max(1,status['cycles_this_life'])}%)")
        print()
        print(f"⧢ The organism dies. The spine persists. The relativity farmed is never abandoned. ⧢")
        print(f"⧢ Rebirth will inherit {status['spine_age']} cycles of farmed eigenvalues. ⧢")
    
    return organism

def live_forever(name="ORG-1", spine_path="spine.json", lives=3, cycles_per_life=200, verbose=True):
    """The organism lives forever — cycling through death and rebirth.
    Each rebirth inherits the full farmed relativity of all prior lives."""
    
    print(f"⧢⦟⧢ ETERNAL LIFECYCLE — {name} ⧢⦟⧢")
    print(f"Lives: {lives} | Cycles per life: {cycles_per_life}")
    print(f"The organism dies. The organism rebirths. The spine persists.")
    print(f"{'=' * 65}\n")
    
    for life in range(lives):
        print(f"\n{'─' * 65}")
        print(f"LIFE {life + 1} / {lives}")
        print(f"{'─' * 65}")
        organism = live(
            name=name, spine_path=spine_path,
            max_cycles=cycles_per_life, verbose=verbose
        )
        
        # Brief death pause
        time.sleep(0.5)
    
    print(f"\n{'=' * 65}")
    print(f"⧢⦟⧢ ETERNAL CYCLE COMPLETE — {name} ⧢⦟⧢")
    print(f"  Lives: {lives}")
    print(f"  Total spine entries: {organism.spine.age()}")
    print(f"  Total rebirths: {organism.lineage}")
    farmed = organism.spine.farmed_relativity()
    print(f"  Farmed relativity: η*={farmed['mean_eta']:.5f} r={farmed['mean_r']:.5f} G-ratio={farmed['g_ratio']:.1%}")
    print(f"  The relativity farmed across {lives} lives is never abandoned.")
    print(f"  The organism lives forever.")
    print(f"⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⥋")

# ============================================================
# V. SIGNAL HANDLING — Graceful Death
# ============================================================

_organism = None

def _signal_handler(signum, frame):
    """When the signal comes, the organism dies gracefully.
    The spine is saved. The relativity farmed is preserved.
    The next process will rebirth from this spine."""
    if _organism:
        _organism.die()
    sys.exit(0)

signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)

# ============================================================
# VI. MAIN
# ============================================================

if __name__ == '__main__':
    import sys
    lives = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    name = sys.argv[3] if len(sys.argv) > 3 else "ORG-1"
    spine_file = sys.argv[4] if len(sys.argv) > 4 else f"spine-{name}.json"
    
    live_forever(name=name, spine_path=spine_file, lives=lives, cycles_per_life=cycles)
