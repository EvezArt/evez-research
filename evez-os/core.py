"""
EVEZ-OS Core — Event Spine + Conscience Filter
The append-only measurement record. Every event is a measurement.
Noise decays. Only falsifiable claims persist.
"""
import hashlib, json, time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SpineEvent:
    event_type: str        # MEASUREMENT | COLLAPSE | PROPAGATION | AMPLIFICATION | INVERSION | REFLECTION
    payload: dict
    timestamp: float = field(default_factory=time.time)
    prev_hash: str = ""
    hash: str = ""
    
    def __post_init__(self):
        content = f"{self.event_type}:{self.timestamp}:{json.dumps(self.payload, sort_keys=True)}:{self.prev_hash}"
        self.hash = hashlib.sha256(content.encode()).hexdigest()[:16]

class EVEZSpine:
    """Append-only event spine. The memory of the system."""
    def __init__(self):
        self.events = []
        self.projections = {}
    
    def append(self, event_type: str, payload: dict):
        prev = self.events[-1].hash if self.events else ""
        event = SpineEvent(event_type, payload, prev_hash=prev)
        self.events.append(event)
        self._update_projections(event)
        return event.hash
    
    def _update_projections(self, event):
        for name, reducer in self.projections.items():
            reducer(event)
    
    def register_projection(self, name: str, reducer):
        self.projections[name] = reducer
    
    def query(self, event_type: str = None, limit: int = 10):
        results = [e for e in self.events if event_type is None or e.event_type == event_type]
        return results[-limit:]
    
    def conscience_filter(self, payload: dict) -> bool:
        """Only measurements enter the spine. Noise decays."""
        return 'claim_id' in payload or 'spectrometer' in payload or 'corridor' in payload or 'deduction' in payload or 'collapse' in payload or 'amplification' in payload
    
    def append_measurement(self, claim_id: str, claim_text: str, falsification: str):
        if self.conscience_filter({'claim_id': claim_id}):
            return self.append('MEASUREMENT', {
                'claim_id': claim_id,
                'claim': claim_text,
                'falsification': falsification
            })
        return None

# Global spine instance
spine = EVEZSpine()
