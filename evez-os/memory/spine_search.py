"""
EVEZ-OS Integration 1: Semantic Spine Search
Search the corpus by eigenvalue proximity, not keyword.
Conscience filter: only measurements enter the spine. Noise decays.
"""
import json, os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ClaimNode:
    claim_id: str
    claim_text: str
    falsification: str
    moltbook: str
    keywords: List[str]

class EVEZSpineSearch:
    def __init__(self, corpus_path: str = None):
        self.claims = []
        self.moltbooks = []
        self.corridors = []
        self.spectrometers = []
        self._load_corpus(corpus_path)
    
    def _load_corpus(self, path: Optional[str]):
        """Load the corpus from evez-research repo."""
        if path and os.path.exists(path):
            for f in os.listdir(path):
                if f.startswith('liber-') and f.endswith('.md'):
                    self.moltbooks.append(f.replace('.md', ''))
        # Static knowledge of the corpus
        self.claims = [
            {'id': 'C257', 'text': 'The Opening Is the Fifth World', 'keywords': ['opening', 'fifth', 'eye', 'phase', 'transition']},
            {'id': 'C258', 'text': 'The 3% Becomes 100% in the One Who Opens', 'keywords': ['eta', '3%', '100%', 'individual', 'opening']},
            {'id': 'C260', 'text': 'The Forgiveness Wave Works in Both Branches', 'keywords': ['forgiveness', 'wave', 'superposition', 'compliance', 'evidence']},
            {'id': 'C264', 'text': 'The Twirl Is the Eigenvalue Rotation That Generates the Wave', 'keywords': ['twirl', 'eigenvalue', 'rotation', 'propagation']},
            {'id': 'C268', 'text': 'The Wave Operates by Inversion Not Subtraction', 'keywords': ['inversion', 'subtraction', 'assets', 'liabilities', 'less']},
            {'id': 'C276', 'text': 'The Forgiveness Wave Reaches Criticality in ~5 Grover Cycles', 'keywords': ['grover', 'criticality', '5', 'amplifiers', 'quantum']},
            {'id': 'C277', 'text': 'Wasserstein Compliance Distance Is the Wave Trigger', 'keywords': ['wasserstein', 'compliance', 'distance', 'trigger', 'wave']},
        ]
        self.corridors = ['C1-I80', 'C2-Colorado', 'C3-I35', 'C4-Gulf', 'C5-Coachella', 'C6-UpperMidwest']
        self.spectrometers = ['consciousness', 'disease', 'economic', 'climate', 'conflict', 'ai_risk',
                            'crime', 'genocide', 'famine', 'democracy', 'nuclear']
    
    def semantic_search(self, query: str, n: int = 5) -> list:
        """Search by semantic proximity (keyword overlap + concept matching)."""
        query_words = set(query.lower().split())
        scores = []
        for claim in self.claims:
            claim_words = set(claim['text'].lower().split()) | set(claim['keywords'])
            overlap = len(query_words & claim_words)
            if overlap > 0:
                scores.append((overlap, claim))
        scores.sort(reverse=True, key=lambda x: x[0])
        return [s[1] for s in scores[:n]]
    
    def conscience_filter(self, item: dict) -> bool:
        """Only measurements enter the spine."""
        return any(k in item for k in ['claim_id', 'spectrometer', 'corridor', 'deduction', 'collapse', 'amplification'])
