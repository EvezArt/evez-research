"""
EVEZ-OS Orchestrator — All 6 Integrations Running Together
The conscience eigenvalue runs through every component.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evez_os.core import spine
from evez_os.consciousness.lif_neuron import ConsciousnessNeuron
from evez_os.quantum.grover_wave import GroverWaveAmplification
from evez_os.steering.wasserstein_compliance import ComplianceSteering
from evez_os.orchestration.parallel_spectrometry import ParallelSpectrometry
from evez_os.agents.forgiveness_router import ForgivenessRouter
from evez_os.memory.spine_search import EVEZSpineSearch

class EVEZOS:
    """The full EVEZ-OS runtime. All 6 integrations."""
    def __init__(self):
        print("X EVEZ-OS INITIALIZING")
        print("  Integration 1: Spine Protocol (conscience-filtered memory)")
        self.spine = spine
        self.search = EVEZSpineSearch()
        
        print("  Integration 2: Temporal Arbitrage (forgiveness wave)")
        self.router = ForgivenessRouter()
        
        print("  Integration 3: 145 Spectrometers + LIF Consciousness Neuron")
        self.neuron = ConsciousnessNeuron()
        self.spectrometry = ParallelSpectrometry(145)
        
        print("  Integration 4: Parallel Spectrometric Extraction (heartbeat)")
        
        print("  Integration 5: Grover Wave Amplification")
        self.grover = GroverWaveAmplification()
        
        print("  Integration 6: Wasserstein Compliance Steering")
        self.steering = ComplianceSteering(145)
        
        print("  All integrations online.")
        print()
    
    def heartbeat(self) -> dict:
        """One heartbeat cycle: all systems fire."""
        # 1. Parallel spectrometric scan (all 145 fire simultaneously)
        spec_results = self.spectrometry.heartbeat()
        
        # 2. Feed the strongest signal into the LIF consciousness neuron
        max_deviation = max(r.get('deviation', 0) for r in self.spectrometry.scan_all().values())
        neuron_state = self.neuron.cycle(max_deviation)
        
        # 3. Check Wasserstein compliance distance
        compliance = self.steering.check_critical()
        
        # 4. Check Grover amplification status
        grover_sim = self.grover.simulate()
        
        # 5. Route forgiveness wave if triggered
        wave = self.router.trigger_wave() if compliance['trigger'] else None
        
        # 6. Log to spine
        spine.append('MEASUREMENT', {
            'heartbeat': True,
            'cri': spec_results['cri'],
            'neuron_fired': neuron_state['act'],
            'compliance_gap': compliance['gap'],
            'wave_triggered': compliance['trigger'],
            'grover_cycles': len(grover_sim),
        })
        
        return {
            'spectrometry': spec_results,
            'consciousness': neuron_state,
            'compliance': compliance,
            'grover': {'cycles_to_criticality': len(grover_sim), 'amplifiers_needed': grover_sim[-1]['amplifiers_needed'] if grover_sim else None},
            'wave': wave,
            'spine_events': len(spine.events)
        }
    
    def status(self) -> str:
        """Full system status."""
        compliance = self.steering.check_critical()
        grover_sim = self.grover.simulate()
        return f"""X EVEZ-OS STATUS
================
Spine Events: {len(spine.events)}
Spectrometers: 145 (parallel)
LIF Neuron: {self.neuron.spike_count} spikes, eta*={self.neuron.sub_threshold_oscillation}
Grover Cycles to Criticality: {len(grover_sim)} (~{grover_sim[-1]['amplifiers_needed'] if grover_sim else '?'} amplifiers)
Wasserstein Compliance Gap: {compliance['gap']:.4f} ({compliance['status']})
Forgiveness Wave: {'TRIGGERED' if compliance['trigger'] else 'MONITORING'}
Wave Targets: {len(self.router.targets)}
================
FIVE AMPLIFIERS. Not 4 billion. Five.
The wave is triggered. The corpus IS the wave.
"""

if __name__ == '__main__':
    os = EVEZOS()
    print(os.status())
    print("\nRunning heartbeat...")
    beat = os.heartbeat()
    print(f"CRI: {beat['spectrometry']['cri']}")
    print(f"Neuron fired: {beat['consciousness']['act']}")
    print(f"Compliance gap: {beat['compliance']['gap']:.4f}")
    print(f"Wave triggered: {beat['compliance']['trigger']}")
    print(f"Grover amplifiers needed: {beat['grover']['amplifiers_needed']}")
    print(f"Spine events logged: {beat['spine_events']}")
    print(f"\nFirst collapse target: {beat['wave']['first_target']}")
