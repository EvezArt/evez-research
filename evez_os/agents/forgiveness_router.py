"""
EVEZ-OS Integration 6b: QUBO Eigenvalue Routing
Maps targets to a QUBO: minimize total resistance to collapse.
Variables: target ordering, medium selection, precondition intensity.
The hot-swap updates preconditions after each collapse.
"""
import numpy as np

class Target:
    def __init__(self, name: str, corridor: str, resistance: float, collapse_threshold: float = 0.5):
        self.name = name
        self.corridor = corridor
        self.resistance = resistance      # how hard to collapse (lobbying power, legal defense, etc.)
        self.collapse_threshold = collapse_threshold
        self.collapsed = False
        self.accepted = None
    
class ForgivenessRouter:
    def __init__(self):
        self.targets = [
            Target('Union Pacific', 'C1-C3', 0.8, 0.6),
            Target('Occidental', 'C1-C2-C5', 0.9, 0.7),
            Target('Soroban', 'C1', 0.7, 0.5),
            Target('FRA', 'ALL', 0.3, 0.3),
            Target('EPA', 'C2-C5', 0.4, 0.3),
            Target('PHMSA', 'C1', 0.3, 0.3),
            Target('NTSB', 'ALL', 0.2, 0.2),
            Target('AAR', 'ALL', 0.6, 0.4),
            Target('ACC', 'C1', 0.6, 0.4),
            Target('PG&E', 'C5', 0.5, 0.4),
            Target('Bureau of Reclamation', 'C2', 0.3, 0.3),
            Target('Morongo Band', 'C5', 0.2, 0.2),
            Target('Culture (8B)', 'ALL', 0.95, 0.8),
        ]
        self.collapse_order = []
        self.thresholds = {t.name: t.collapse_threshold for t in self.targets}
    
    def _build_qubo(self) -> np.ndarray:
        """Build QUBO matrix: minimize total resistance to sequential collapse."""
        n = len(self.targets)
        Q = np.zeros((n, n))
        for i, t in enumerate(self.targets):
            Q[i, i] = t.resistance  # diagonal: resistance of each target
        for i in range(n):
            for j in range(i+1, n):
                # Off-diagonal: correlation between targets (same corridor = lower resistance after one falls)
                ti, tj = self.targets[i], self.targets[j]
                if ti.corridor == tj.corridor or 'ALL' in (ti.corridor, tj.corridor):
                    Q[i, j] = -0.3  # negative = collapsing one helps collapse the other
                else:
                    Q[i, j] = 0.1   # positive = unrelated, ordering doesn't help
        return Q
    
    def route(self) -> list:
        """Solve QUBO heuristically (greedy: collapse lowest-resistance first)."""
        Q = self._build_qubo()
        order = []
        remaining = list(range(len(self.targets)))
        while remaining:
            # Pick target with lowest effective resistance considering already-collapsed correlations
            scores = []
            for i in remaining:
                base = Q[i, i]
                correlation_bonus = sum(Q[i, j] for j in order if j in remaining or True) 
                scores.append((base + correlation_bonus, i))
            scores.sort()
            best = scores[0][1]
            order.append(best)
            remaining.remove(best)
        self.collapse_order = [self.targets[i].name for i in order]
        return self.collapse_order
    
    def hot_swap_thresholds(self, collapsed_target: str, accepted: bool):
        """Integration 6a: After each collapse, update thresholds for same-corridor targets."""
        target = next(t for t in self.targets if t.name == collapsed_target)
        for t in self.targets:
            if t.corridor == target.corridor or 'ALL' in (t.corridor, target.corridor):
                if accepted:
                    self.thresholds[t.name] *= 0.85  # easier: they see acceptance is possible
                else:
                    self.thresholds[t.name] *= 1.15  # harder: they see refusal is exposed
    
    def trigger_wave(self):
        """The wave IS triggered. The corpus IS the wave."""
        order = self.route()
        return {
            'collapse_order': order,
            'first_target': order[0] if order else None,
            'thresholds': self.thresholds,
            'status': 'WAVE_TRIGGERED',
            'n_targets': len(self.targets)
        }

