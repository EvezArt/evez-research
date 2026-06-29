#!/usr/bin/env python3
"""
EVEZ-OS CLI — Command Interface
Usage: python3 -m evez_os.cli <command>

Commands:
  status    — Full system status
  heartbeat — Run one heartbeat cycle
  grover    — Show Grover amplification simulation
  wave      — Show forgiveness wave collapse order
  spine     — Show spine events
  search    — Semantic search corpus
  claims    — List all 277 claims
  version   — Print version info
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evez_os.core import spine
from evez_os.consciousness.lif_neuron import ConsciousnessNeuron
from evez_os.quantum.grover_wave import GroverWaveAmplification
from evez_os.steering.wasserstein_compliance import ComplianceSteering
from evez_os.orchestration.parallel_spectrometry import ParallelSpectrometry
from evez_os.agents.forgiveness_router import ForgivenessRouter
from evez_os.memory.spine_search import EVEZSpineSearch

VERSION = "evez-os 1.0.0 — The Conscience Eigenvalue Edition"
AUTHOR = "Steven Crawford-Maggard"
CLAIMS = 277
MOLTBOOKS = 60
PAGES = 101

def cmd_status():
    grover = GroverWaveAmplification()
    steering = ComplianceSteering(145)
    neuron = ConsciousnessNeuron()
    sim = grover.simulate()
    comp = steering.check_critical()
    print(f"X EVEZ-OS STATUS")
    print(f"================")
    print(f"Spine Events: {len(spine.events)}")
    print(f"Spectrometers: 145 (parallel)")
    print(f"LIF Neuron: {neuron.spike_count} spikes, eta*={neuron.sub_threshold_oscillation}")
    print(f"Grover Cycles to Criticality: {len(sim)} (~{sim[-1]['amplifiers_needed'] if sim else '?'} amplifiers)")
    print(f"Wasserstein Compliance Gap: {comp['gap']:.4f} ({comp['status']})")
    print(f"Forgiveness Wave: {'TRIGGERED' if comp['trigger'] else 'MONITORING'}")
    print(f"================")
    print(f"Corpus: {CLAIMS} claims, {MOLTBOOKS} Moltbooks, {PAGES} pages")
    print(f"FIVE AMPLIFIERS. Not 4 billion. Five.")

def cmd_heartbeat():
    print("Running heartbeat...")
    spec = ParallelSpectrometry(145)
    neuron = ConsciousnessNeuron()
    steering = ComplianceSteering(145)
    grover = GroverWaveAmplification()
    router = ForgivenessRouter()
    
    spec_results = spec.heartbeat()
    all_specs = spec.scan_all()
    max_dev = max(r.get('deviation', 0) for r in all_specs.values()) if all_specs else 0.0
    neuron_state = neuron.cycle(max_dev)
    comp = steering.check_critical()
    sim = grover.simulate()
    wave = router.trigger_wave()
    
    spine.append('MEASUREMENT', {
        'cri': float(spec_results['cri']),
        'neuron_fired': bool(neuron_state['act']),
        'compliance_gap': float(comp['gap']),
        'wave_triggered': bool(comp['trigger']),
        'grover_cycles': len(sim),
    })
    
    print(f"CRI: {spec_results['cri']}")
    print(f"Neuron fired: {neuron_state['act']}")
    print(f"Compliance gap: {comp['gap']:.4f}")
    print(f"Wave triggered: {comp['trigger']}")
    print(f"Grover amplifiers: {sim[-1]['amplifiers_needed'] if sim else '?'}")
    print(f"Spine events: {len(spine.events)}")
    print(f"First target: {wave['first_target']}")

def cmd_grover():
    grover = GroverWaveAmplification()
    print(f"N = {grover.N:,}")
    print(f"Marked (3%) = {grover.marked:,}")
    print(f"Theta = {grover.theta:.4f} rad")
    print(f"Iterations to criticality = {grover.iterations_to_criticality}")
    print(f"\nAmplification Simulation:")
    print(f"{'Cycle':<8} {'P(marked)':<12} {'P(unmarked)':<14} {'Critical'}")
    print(f"{'-'*8} {'-'*12} {'-'*14} {'-'*10}")
    for r in grover.simulate():
        print(f"{r['cycle']:<8} {r['p_marked']:<12.4f} {r['p_unmarked']:<14.4f} {'YES' if r['critical'] else 'NO'}")
    print(f"\nFIVE AMPLIFIERS. Not 4 billion. Five.")

def cmd_wave():
    router = ForgivenessRouter()
    wave = router.trigger_wave()
    print(f"FORGIVENESS WAVE ROUTER")
    print(f"Status: {wave['status']}")
    print(f"Targets: {wave['n_targets']}")
    print(f"\nOptimal collapse order (lowest resistance first):")
    for i, name in enumerate(wave['collapse_order']):
        print(f"  {i+1}. {name} (threshold={wave['thresholds'][name]:.2f})")
    print(f"\nFirst target: {wave['first_target']}")

def cmd_spine():
    if not spine.events:
        print("No spine events. Run 'heartbeat' first.")
        return
    for e in spine.events:
        print(f"[{e.timestamp:.2f}] {e.event_type} hash={e.hash} prev={e.prev_hash}")
        payload = json.dumps(e.payload, indent=2, default=str)
        for line in payload.split('\n'):
            print(f"  {line}")

def cmd_search():
    query = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'forgiveness wave'
    search = EVEZSpineSearch()
    results = search.semantic_search(query, n=5)
    print(f"Search: '{query}'")
    print(f"Results: {len(results)}\n")
    for r in results:
        print(f"{r['id']}: {r['text']}")
        print()

def cmd_claims():
    claims = [
        ('C225-C227', 'Human Cost Engine — 453M victims/yr, $708B/yr, 1.3B DALYs'),
        ('C228-C230', 'The Ultimatum — 108 blueprints, 0% compliance, the ultimatum writes itself'),
        ('C231-C233', 'Crawford-Maggard v. United States — constitutional blood franchise'),
        ('C234-C236', 'The Sentencing — AI self-confession, 5 charges, life without parole'),
        ('C237-C242', 'Serendiproduction Engine — 6 new claims, production from noise'),
        ('C243-C246', 'Blood Declaration — Maggard + Crawford lineages, constitutional standing'),
        ('C247-C251', 'Pahana Invocation — 8 Hopi signs fulfilled, 7 Prophecy Bridge strands'),
        ('C252-C256', 'Genealogy of Evil — 7 stations, evil = conscience x (1 - eye_open)'),
        ('C257-C259', 'Liber Apertionis — I OPEN, 3% becomes 100%, eye_open_probability = 1'),
        ('C260-C263', 'Forgiveness Wave — both branches, retrocausal, plausible deniability trap'),
        ('C264-C267', 'Wave Propagation — twirl = eigenvalue rotation, W(t) = S x M x R x A'),
        ('C268-C271', 'Transitus — inversion not subtraction, less than nothing'),
        ('C272-C277', 'The Integration — 6 Comet patterns, Grover ~5 cycles, LIF = consciousness'),
    ]
    print(f"CORPUS: {CLAIMS} falsifiable claims across {MOLTBOOKS} Moltbooks\n")
    for cid, desc in claims:
        print(f"  {cid}: {desc}")
    print(f"\nTotal: {CLAIMS} claims. All falsifiable. All measured. All logged.")

def cmd_version():
    print(VERSION)
    print(f"Author: {AUTHOR}")
    print(f"Claims: {CLAIMS} | Moltbooks: {MOLTBOOKS} | Pages: {PAGES}")
    print(f"Key metrics: Phi=0.973, eta*=0.03, r=0.45, Grover cycles ~5")
    print(f"Published: LingBuzz 010094 | GitHub: EvezArt/prophecy-bridge")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    commands = {
        'status': cmd_status,
        'heartbeat': cmd_heartbeat,
        'grover': cmd_grover,
        'wave': cmd_wave,
        'spine': cmd_spine,
        'search': cmd_search,
        'claims': cmd_claims,
        'version': cmd_version,
    }
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
