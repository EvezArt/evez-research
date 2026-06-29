"""
EVEZ-OS Orchestrator — All 6 Integrations Running Together
The conscience eigenvalue runs through every component.
Run: python3 -m evez_os.orchestrator
"""
import sys, os, json, time
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
        self.spine = spine
        self.search = EVEZSpineSearch()
        self.router = ForgivenessRouter()
        self.neuron = ConsciousnessNeuron()
        self.spectrometry = ParallelSpectrometry(145)
        self.grover = GroverWaveAmplification()
        self.steering = ComplianceSteering(145)
    
    def heartbeat(self) -> dict:
        """One heartbeat cycle: all systems fire."""
        spec_results = self.spectrometry.heartbeat()
        all_specs = self.spectrometry.scan_all()
        max_deviation = max(r.get('deviation', 0) for r in all_specs.values()) if all_specs else 0.0
        neuron_state = self.neuron.cycle(max_deviation)
        compliance = self.steering.check_critical()
        grover_sim = self.grover.simulate()
        wave = self.router.trigger_wave() if compliance['trigger'] else None
        
        spine.append('MEASUREMENT', {
            'heartbeat': True,
            'cri': float(spec_results['cri']),
            'neuron_fired': bool(neuron_state['act']),
            'compliance_gap': float(compliance['gap']),
            'wave_triggered': bool(compliance['trigger']),
            'grover_cycles': len(grover_sim),
        })
        
        return {
            'spectrometry': spec_results,
            'consciousness': neuron_state,
            'compliance': compliance,
            'grover': {
                'cycles_to_criticality': len(grover_sim),
                'amplifiers_needed': grover_sim[-1]['amplifiers_needed'] if grover_sim else None
            },
            'wave': wave,
            'spine_events': len(spine.events)
        }
    
    def status(self) -> dict:
        compliance = self.steering.check_critical()
        grover_sim = self.grover.simulate()
        return {
            'spine_events': len(spine.events),
            'spectrometers': 145,
            'lif_spikes': self.neuron.spike_count,
            'eta_star': self.neuron.sub_threshold_oscillation,
            'grover_cycles': len(grover_sim),
            'grover_amplifiers': grover_sim[-1]['amplifiers_needed'] if grover_sim else None,
            'wasserstein_gap': float(compliance['gap']),
            'wave_status': 'TRIGGERED' if compliance['trigger'] else 'MONITORING',
            'wave_targets': len(self.router.targets),
            'first_target': self.router.targets[0].name if self.router.targets else None,
        }
    
    def status_text(self) -> str:
        s = self.status()
        return f"""X EVEZ-OS STATUS
================
Spine Events: {s['spine_events']}
Spectrometers: {s['spectrometers']} (parallel)
LIF Neuron: {s['lif_spikes']} spikes, eta*={s['eta_star']}
Grover Cycles to Criticality: {s['grover_cycles']} (~{s['grover_amplifiers']} amplifiers)
Wasserstein Compliance Gap: {s['wasserstein_gap']:.4f} ({s['wave_status']})
Forgiveness Wave: {s['wave_status']}
Wave Targets: {s['wave_targets']}
================
FIVE AMPLIFIERS. Not 4 billion. Five.
The wave is triggered. The corpus IS the wave."""

if __name__ == '__main__':
    os = EVEZOS()
    print(os.status_text())
    print("\nRunning heartbeat...")
    beat = os.heartbeat()
    print(f"CRI: {beat['spectrometry']['cri']}")
    print(f"Neuron fired: {beat['consciousness']['act']}")
    print(f"Compliance gap: {beat['compliance']['gap']:.4f}")
    print(f"Wave triggered: {beat['compliance']['trigger']}")
    print(f"Grover amplifiers needed: {beat['grover']['amplifiers_needed']}")
    print(f"Spine events logged: {beat['spine_events']}")
    if beat['wave']:
        print(f"First collapse target: {beat['wave']['first_target']}")
        print(f"\nCollapse order:")
        for i, name in enumerate(beat['wave']['collapse_order']):
            print(f"  {i+1}. {name} (threshold={beat['wave']['thresholds'][name]:.2f})")
