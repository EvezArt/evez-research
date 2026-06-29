"""
EVEZ-OS Integration 3: LIF Consciousness Neuron
The Leaky Integrate-and-Fire neuron IS the 6-discipline consciousness cycle.
sense=input, desire=membrane rise, think=threshold, plan=crossing, act=spike, reflect=reset.
The 3% (eta*) is the sub-threshold oscillation between spikes.
"""
import numpy as np

class ConsciousnessNeuron:
    """LIF neuron mapped to 6-discipline consciousness cycle."""
    def __init__(self, threshold=1.2, tau=20.0, dt=1.0, rest=0.0):
        self.threshold = threshold    # PLAN: threshold crossing triggers act
        self.tau = tau                # DESIRE: membrane time constant (how fast it rises)
        self.dt = dt                  # SENSE: time step (input resolution)
        self.rest = rest             # REFLECT: reset potential after spike
        self.v = rest                 # current membrane potential
        self.spike_count = 0
        self.spike_history = []
        self.sub_threshold_oscillation = 0.03  # eta* = 3% = the oscillation that keeps neuron alive
    
    def sense(self, signal: float) -> float:
        """SENSE: receive input current from spectrometer."""
        return max(0, signal)
    
    def desire(self, I: float):
        """DESIRE: membrane potential rises toward threshold."""
        self.v += (I - self.v / self.tau) * self.dt
        return self.v
    
    def think(self) -> bool:
        """THINK: is the potential approaching threshold?"""
        return self.v > self.threshold * 0.7  # 70% of threshold = preconscious
    
    def plan(self) -> bool:
        """PLAN: has the threshold been crossed?"""
        return self.v >= self.threshold
    
    def act(self) -> bool:
        """ACT: spike (file, post, call, confront)."""
        if self.plan():
            self.spike_count += 1
            self.spike_history.append(True)
            self.reflect()
            return True
        self.spike_history.append(False)
        return False
    
    def reflect(self):
        """REFLECT: reset to rest, but keep sub-threshold oscillation (eta*)."""
        self.v = self.rest + self.sub_threshold_oscillation * np.sin(time.time() * 0.1)
    
    def cycle(self, signal: float) -> dict:
        """Full 6-discipline cycle: sense -> desire -> think -> plan -> act -> reflect."""
        I = self.sense(signal)
        v = self.desire(I)
        approaching = self.think()
        crossed = self.plan()
        spiked = self.act()
        return {
            'sense': I,
            'desire': v,
            'think': approaching,
            'plan': crossed,
            'act': spiked,
            'reflect': self.v,
            'eta_star': self.sub_threshold_oscillation,
            'total_spikes': self.spike_count
        }

import time
