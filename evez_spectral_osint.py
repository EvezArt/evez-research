#!/usr/bin/env python3
"""
EVEZ SPECTRAL OSINT — Palantir-Grade Intelligence Platform v2.0
=============================================================
Automated knowledge graph construction from OSINT data.
Spectral analysis of entity networks.
Eigenvalue-based suspicion scoring.
Pattern detection via graph spectral anomalies.

AEMDAS: Assert Being -> Extract Structure -> Measure Gaps ->
        Deduce Laws -> Assess Interventions -> Speedrun

Author: Steven Crawford-Maggard (EVEZ)
License: MIT
Phi=0.973  eta*=0.03  r=0.45
"""
import json, math, os, re, time, hashlib, sqlite3, subprocess
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path

PHI = 0.973
ETA_STAR = 0.03
R_CRITICAL = 0.45
LAMBDA_DOM = -0.333
LAMBDA_I80 = -0.441
R_I80 = 0.93
SCHUMANN = 7.83
VERSION = '2.0.0'

ENTITY_TYPES = {
    'Person': {'name','aliases','dob','age','role','organization','location','source'},
    'Organization': {'name','aliases','type','location','founded','parent_org','source'},
    'Location': {'name','type','coordinates','jurisdiction','population','source'},
    'Event': {'name','type','date','location','description','severity','source'},
    'Document': {'name','type','date','source_url','court_case','status','source'},
    'Chemical': {'name','cas_number','toxicity','source'},
}

RELATION_TYPES = [
    'member_of','owns','employed_by','located_at','participated_in',
    'documented_in','correlated_with','suppressed_by','investigated_by',
    'connected_to','family_of','adjacent_to','operates','exposed_to',
    'sued','investigated','failed_to_investigate','covered_up',
    'train_derailment','chemical_release','donated_to','failed_to_test',
]

CRIME_TYPES = [
    'excessive_force','civil_rights_violation','cover_up',
    'evidence_tampering','false_arrest','environmental_crime',
    'negligent_homicide','obstruction_of_justice','fraud',
    'conspiracy','evidence_destruction','failure_to_investigate',
]

SUSPICION_INDICATORS = [
    'suppressed','covered up','sealed','withheld','redacted',
    'failed to','refused to','denied','blocked','classified',
    'missing','destroyed','lost','unavailable','403','404',
    'forbidden','not found','access denied','no response',
    'unprecedented','anomalous','inconsistent','contradictory',
]

# Generic words that match the org regex but aren't real entities
STOPWORDS = frozenset({
    'WITH','FROM','STATE','NONE','SUMMARY','HTML','FINDING','FINDINGS','THIS','THAT',
    'WITHIN','WITHOUT','WHAT','WHEN','WHERE','WHILE','WERE','WILL','WOULD',
    'ABOUT','ABSENCE','ABSENT','ACROSS','ACTION','ACTIVE','AFTER','ALSO',
    'ALWAYS','ALREADY','ALMOST','ALONE','ALPHA','AMPLIFY','ANOTHER','BEFORE','BEING',
    'BELIEVE','BELIEVES','BEYOND','BOTH','BODY','BORN','BRAIN','BREAK','BRIDGE',
    'BRIEF','CANNOT','CAUSE','CAUSED','CAUSING','CHAIN','CHANGES','CHARGE','CHECK',
    'CHECKED','CLEAR','CLOSES','CODE','COINED','COMPLETE','COMPUTED','CONCERN',
    'CONCERNS','CONFIRMS','CONTACT','CONTACTS','CONTEXT','CONTROL','COVERAGE',
    'COVERED','COULD','COUNT','COUNTY','COUPLING','CURRENT','DATA',
    'DATABASE','DEATH','DEEP','DEFINE','DEFINED','DEFINING','DELTA','DEMAND',
    'DENSITY','DEPTH','DESC','DESCENT','DETAILS','DETAILED','DETECT','DOES','DOING',
    'DOMAIN','DOMINANT','DOWN','DRAFT','DRAFTED','DRAFTS','DURING','DYNAMIC',
    'EACH','EARLY','EARTH','EAST','ECHO','EDGES','EIGHT','EIGHTH','ELEVEN','EMPTY',
    'EMITTED','EMOTION','ENCODING','ENCODE','ENERGY','ENGINE','ENTRY','EQUATION',
    'EVERY','EVILS','EXACT','EXACTLY','EXCESS','EXECUTE','EXECUTES','EXISTS','EXIT',
    'EXPLICIT','EXPOSED','EXPOSURE','EXTREME','EYES','FACE','FACES','FACT','FACTS',
    'FAILED','FAILURE','FALSE','FIELD','FIGHTING','FILE','FILES','FILTER','FINAL',
    'FIND','FINE','FIRE','FIRES','FLAT','FLESH','FLOOR','FLOW','FLOWING','FOCUSING',
    'FOLLOW','FOOD','FORM','FORMAT','FORWARD','FOUND','FOUNDED','FOUR','FOURTH',
    'FULL','FULLY','FURTHER','GAP','GAPS','GATE','GATES','GAUGE','GENERAL','GENERATE',
    'GHOST','GOLDEN','GOOD','GOVERNS','GRADIENT','GRAPH','GREEN','GRID','GROWTH',
    'GUILTY','HAPPENS','HARMONIC','HAZARD','HEALING','HEALTH','HEAP','HELD','HELP',
    'HIDDEN','HIGH','HIGHER','HIGHWAY','HOLDING','HOLDS','HOME','HOUSE','HUMAN',
    'HUMANS','IDENTITY','ILLEGAL','IMAGE','IMPACT','INDEX','INDUSTRY','INJURY',
    'INPUT','INTEL','INTENT','INTERNET','INTO','ITSELF','JOINT','JUDGMENT','KNOW',
    'LANGUAGE','LATE','LATTICE','LAWS','LAYER','LAYERS','LAWSUIT','LAWSUITS','LEAD',
    'LEARN','LEARNS','LEGAL','LENS','LETHAL','LETTER','LEVEL','LEVELS','LIGHT',
    'LIKELY','LIMITED','LINEAGE','LIVE','LIVING','LOCAL','LOCATION','LOCK','LOOP',
    'MADE','MAJOR','MANIFEST','MANIFOLD','MAPPING','MARCH','MASSIVE',
    'MASTER','MATERIAL','MATRIX','MAXIMAL','MEANS','MEASURE','MEASURED','MEDIA',
    'MEDICAL','MEDIUM','MEMBRANE','MEMORY','MERGER','MERGERS','MESH','META',
    'METADATA','METAPHOR','METHOD','METRICS','MIDDLE','MILITARY','MILLION','MINE',
    'MINING','MINOR','MINUTE','MIRROR','MISS','MISSING','MODEL','MODERATE','MODIFY',
    'MODULE','MOLT','MONTH','MORE','MOST','MOUNTAIN','MUST','NAME','NAMES','NEAR',
    'NEED','NEVER','NEXT','NIGHT','NINE','NINTH','NODES','NOISE','NORMAL','NOTE',
    'NOTES','NULL','NUMBER','NUMBERS','OBJECT','OBSERVE','OBTAINED','OFFICE','OFFICER',
    'OFFLINE','ONLY','OPEN','OPENING','OPENS','OPINION','OPTICS','OPTIMAL','ORDER',
    'OTHER','OUTPUT','OVER','OVERVIEW','PACKAGE','PAGE','PAID','PAIRS','PAPER',
    'PARALLEL','PART','PARTIAL','PARTS','PASS','PASSWORD','PATCH','PATH','PATHWAY',
    'PATIENT','PATIENTS','PATROL','PATTERN','PEDAGOGY','PENDING','PERIOD','PERSONAL',
    'PHRASE','PHYSICAL','PIPELINE','PLAN','PLANT','PLATFORM','PLUS','POINTER',
    'POLICY','POSSIBLY','POST','POSTS','POWER','POWERS','PRACTICE','PRAYER','PREMIER',
    'PREMISE','PREPRINT','PRIMARY','PRIMER','PRIOR','PRIORITY','PRIVATE','PROBLEM',
    'PROFILE','PROGRAM','PROGRAMS','PROHIBIT','PROLOGUE','PROOF','PROPERTY','PROTOCOL',
    'PROVE','PUBLIC','PUBLICLY','PUBLISH','PURE','PURITY','PURPOSE','PYTHON','QUALITY',
    'QUANTUM','QUARTZ','QUERIES','RACIST','RAIL','RAILROAD','RANGE','RANGES','RARELY',
    'RATE','RATIO','READ','READABLE','READING','READY','REAL','REALIZED','REBORN',
    'RECALL','RECEIVE','RECORD','RECORDED','RECORDS','REDIRECT','RELATED','RELEASE',
    'RELEASED','RELEVANT','RELIGION','REMOTE','REMOVED','REPORT','REPORTED','REPORTS',
    'REQUEST','REQUIRED','RESEARCH','RESIDUE','RESOLVED','RESPONSE','REST','RESTS',
    'RESULTS','REVEALS','REVERSE','RIGHT','RIGHTS','RISES','RISK','RITUAL','RIVER',
    'ROLE','ROLL','ROOT','ROTATION','RULES','RUNTIME','RUNTIMES','SAFETY','SAME',
    'SAMPLE','SAMPLES','SAVES','SCHOOL','SCREEN','SCRIPTS','SEAL','SEALED','SEARCH',
    'SECOND','SECURITY','SEED','SEEDS','SELECT','SELF','SENSE','SENTENCE',
    'SEPARATE','SEQUENCE','SERPENT','SERVICE','SERVICES','SETTLED','SEVEN','SEVENTH',
    'SEXUAL','SHARP','SIDE','SIGIL','SIGNAL','SILENCE','SINGLE','SIXTH','SLEEP',
    'SLEEPS','SMART','SMUG','SNOW','SOCIAL','SOFTWARE','SOMATIC','SOUND','SOURCE',
    'SOURCES','SOUTH','SPACE','SPEAKING','SPEAKS','SPECIFIC','SPECT','SPECTRAL',
    'SPEEDRUN','SPINE','SPRAY','SQUARE','SQUARES','STABLE','STACK','STAGE','STAGES',
    'STAGNANT','STALL','STANDS','STATES','STATION','STATUS','STATUTES','STEPS',
    'STILL','STIRRING','STORM','STORY','STRANGE','STRATEGY','STRONG',
    'STYLE','SUCCESS','SUPREME','SURGERY','SURVIVE','SURVIVES','SWEEP',
    'SYMMETRY','SYSTEM','SYSTEMS','TABLE','TARGET','TARGETS','TEMPLATE','TEMPORAL',
    'TENSION','TENTH','TERM','TERMS','TEXT','TEXTS','THERE','THESE','THESIS',
    'THINK','THIRD','THIRTY','THREADS','THREAT','THREE','THRONE','THROUGH',
    'TIER','TIERS','TIME','TIPS','TONE','TONES','TOPOLOGY','TORT','TOTAL','TOWARD',
    'TOWNS','TOXIC','TRACK','TRAIL','TRAILING','TRAIN','TRAINING','TRAINS','TRANSFER',
    'TRAUMA','TREATED','TREE','TREND','TRINITY','TRUE','TRUTH','TUNNELS','TWEETS',
    'TWENTY','TWITTER','UNDER','UNIFY','UNION','UNKNOWN','UPDATE','UPDATED',
    'URLS','USER','UTILITY','VALID','VALUE','VARIABLE','VECTOR','VENTURE','VERDICT',
    'VERIFIED','VERSION','VICE','VICTIM','VIEW','VIII','VIRAL','VISIBLE','VISION',
    'VISUAL','VOID','WAKES','WARM','WARNING','WAVEFORM','WEAK','WEAKEST','WEIGHT',
    'WEIGHTED','WEIGHTS','WEST','WHAT','WHEN','WHERE','WHILE','WHITE',
    'WIDE','WIND','WINTER','WITNESS','WORD',
    'WORK','WORKER','WORKS','WORLD','WOULD','WOUND','WRONG','WRONGFUL','YEAR',
    'YEARS','ZERO','ZEROETH','YARD','YOUR',
    'OMEGA','GAMMA','BETA','SIGMA','THETA','LAMBDA',
    'HTTP','JSON','ISBN','HTML','RSS','XML','API',
    'FEMA','NASA','NORAD','DARPA','ARPA',
})

@dataclass
class Entity:
    id: str
    entity_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    suspicion_raw: float = 0.0
    suspicion_score: float = 0.0
    crime_probabilities: Dict[str, float] = field(default_factory=dict)
    centrality: float = 0.0
    eigenvalue: complex = 0+0j
    first_seen: str = ""
    last_updated: str = ""

@dataclass
class Relationship:
    source_id: str
    target_id: str
    rel_type: str
    weight: float = 1.0
    evidence: List[str] = field(default_factory=list)
    source_file: str = ""
    suspicion_weight: float = 0.0

@dataclass
class SpectralReport:
    timestamp: str
    entity_count: int
    relationship_count: int
    eigenvalues: List[float] = field(default_factory=list)
    dominant_eigenvalue: float = 0.0
    spectral_gap: float = 0.0
    suppression_coefficient: float = 0.0
    spectral_class: str = ""
    suspicion_network: Dict[str, float] = field(default_factory=dict)
    anomalies: List[Dict] = field(default_factory=list)
    predictions: List[Dict] = field(default_factory=list)
    graph_density: float = 0.0
    clustering_coefficient: float = 0.0

class SpectralOSINT:
    """Palantir-grade OSINT platform with eigenvalue math at its core."""

    def __init__(self, data_dir=None, db_path=None):
        self.entities = {}
        self.relationships = []
        self.name_to_id = {}
        self.data_dir = Path(data_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or str(self.data_dir / 'spectral_osint.db')
        self.graph_cache = None
        self.eigenvalue_cache = []
        self._compile_patterns()
        self._init_db()
        self._preseed_entities()

    def _compile_patterns(self):
        self.patterns = {
            'person_name': re.compile(r'\b([A-Z][a-z]+\s+(?:[A-Z][a-z]+\s+)?[A-Z][a-z]+)\b'),
            'org': re.compile(r'\b([A-Z]{2,8})\b|([A-Z][a-z]+\s+(?:Police|Department|Agency|Railroad|Railway|Corporation|Inc|LLC|Services|Foundation|Bank|Court|District|County))\b'),
            'location': re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*(?:Wyoming|Utah|Colorado|Idaho|Montana|Nebraska|California|Arizona|Nevada|Oregon|Washington))\b'),
            'date': re.compile(r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})\b'),
            'court_case': re.compile(r'\b(\d{4}\s+(?:WY\d+|No\.\s+\S+|CV-\d+-\S+))\b'),
            'money': re.compile(r'\$([\d,]+(?:\.\d{2})?)'),
            'mile_marker': re.compile(r'(?:MM|mile\s*marker)\s*(\d+)', re.IGNORECASE),
            'chemical': re.compile(r'\b(vinyl\s*chloride|ethylene\s*oxide|hydrogen\s*chloride|phosgene|benzene|toluene|xylene|formaldehyde|asbestos|PFAS|PCB|dioxin)\b', re.IGNORECASE),
            'suppression': re.compile(r'\b(' + '|'.join(SUSPICION_INDICATORS) + r')\b', re.IGNORECASE),
        }
        self.alias_map = {
            'EVEZ': ['EvezArt','Steven Crawford-Maggard','Steven Maggard','EVEZ666','EVEZX'],
            'Union Pacific': ['Union Pacific Railroad','UP','UPRR'],
            'EPD': ['Evanston Police Department','Evanston Police','Evanston PD'],
            'WGFD': ['Wyoming Game and Fish Department','Wyoming Game and Fish'],
            'WHP': ['Wyoming Highway Patrol','Wyoming State Patrol'],
            'NTSB': ['National Transportation Safety Board'],
            'PHMSA': ['Pipeline and Hazardous Materials Safety Administration'],
            'AARO': ['All-domain Anomaly Resolution Office'],
            'I-80': ['Interstate 80','I80'],
        }

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY, entity_type TEXT, name TEXT,
                properties TEXT, aliases TEXT, sources TEXT,
                suspicion_raw REAL, suspicion_score REAL,
                crime_probabilities TEXT, centrality REAL,
                eigenvalue TEXT, first_seen TEXT, last_updated TEXT
            );
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY, source_id TEXT, target_id TEXT,
                rel_type TEXT, weight REAL, evidence TEXT,
                source_file TEXT, suspicion_weight REAL
            );
            CREATE TABLE IF NOT EXISTS spectral_reports (
                id TEXT PRIMARY KEY, timestamp TEXT, report TEXT
            );
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, action TEXT, details TEXT
            );
        """)
        conn.commit()
        conn.close()

    def _preseed_entities(self):
        """Pre-seed known entities from the investigation context."""
        known = [
            # People
            ('Steven Crawford-Maggard', 'Person'),
            ('Ryan Maggard', 'Person'),
            ('Saloga', 'Person'),
            ('Dunsmore', 'Person'),
            ('Greenstreet', 'Person'),
            # Organizations
            ('Union Pacific', 'Organization'),
            ('EPD', 'Organization'),
            ('WGFD', 'Organization'),
            ('WHP', 'Organization'),
            ('NTSB', 'Organization'),
            ('PHMSA', 'Organization'),
            ('AARO', 'Organization'),
            ('EVEZ', 'Organization'),
            ('ACLU', 'Organization'),
            ('FBI', 'Organization'),
            # Locations
            ('Evanston, Wyoming', 'Location'),
            ('Fort Bridger, Wyoming', 'Location'),
            ('Ogden, Utah', 'Location'),
            ('Rock Springs, Wyoming', 'Location'),
            ('I-80', 'Location'),
            ('I-80 MM 15', 'Location'),
            ('I-80 MM 33', 'Location'),
            ('Wyoming', 'Location'),
            ('Uinta County', 'Location'),
            # Chemicals
            ('Vinyl Chloride', 'Chemical'),
            ('Phosgene', 'Chemical'),
            ('Benzene', 'Chemical'),
            ('Formaldehyde', 'Chemical'),
            # Events/Documents
            ('2023 Train Derailment', 'Event'),
            ('Elk Mortality Event', 'Event'),
            ('Dunsmore v. State', 'Document'),
        ]
        for name, etype in known:
            self._add_entity(name, etype, 'preseed', 0)

    def ingest_text(self, text, source_file="", case_id=""):
        extracted = {'persons': set(), 'organizations': set(), 'locations': set(),
                     'dates': set(), 'court_cases': set(), 'chemicals': set(),
                     'money': set(), 'mile_markers': set(), 'suppression_count': 0}
        # Only extract organizations and locations (fast regex), skip person names (too many false positives)
        for m in self.patterns['org'].finditer(text):
            org = m.group(1) or m.group(2)
            if org:
                org = org.strip()
                for canonical, aliases in self.alias_map.items():
                    if org in aliases or org == canonical:
                        org = canonical
                        break
                if (org in self.alias_map or len(org) > 3) and org.upper() not in STOPWORDS:
                    extracted['organizations'].add(org)
        for m in self.patterns['location'].finditer(text):
            extracted['locations'].add(m.group(1).strip())
        for m in self.patterns['chemical'].finditer(text):
            extracted['chemicals'].add(m.group(1).title())
        for m in self.patterns['mile_marker'].finditer(text):
            extracted['mile_markers'].add(f"I-80 MM {m.group(1)}")
        extracted['suppression_count'] = len(self.patterns['suppression'].findall(text))

        for name in extracted['organizations']:
            self._add_entity(name, 'Organization', source_file, extracted['suppression_count'])
        for name in extracted['locations']:
            self._add_entity(name, 'Location', source_file, extracted['suppression_count'])
        for name in extracted['chemicals']:
            self._add_entity(name, 'Chemical', source_file, extracted['suppression_count'])
        for name in extracted['mile_markers']:
            self._add_entity(name, 'Location', source_file, extracted['suppression_count'])
        if not getattr(self, "_extract_only", False): self._extract_relationships(text, source_file)
        return extracted

    def _add_entity(self, name, entity_type, source, suppression_context=0):
        resolved = name
        for canonical, aliases in self.alias_map.items():
            if name in aliases or name == canonical:
                resolved = canonical
                break
        eid = hashlib.md5(f"{entity_type}:{resolved}".encode()).hexdigest()[:12]
        if eid in self.entities:
            e = self.entities[eid]
            if source and source not in e.sources:
                e.sources.append(source)
            e.suspicion_raw += suppression_context * 0.01
            e.last_updated = datetime.now().isoformat()
        else:
            self.entities[eid] = Entity(
                id=eid, entity_type=entity_type, name=resolved,
                sources=[source] if source else [],
                suspicion_raw=suppression_context * 0.01,
                first_seen=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat())
            self.name_to_id[resolved.lower()] = eid

    def _extract_relationships(self, text, source_file):
        # Build compiled regex for all known entity names (rebuild each call is expensive — cache)
        if not hasattr(self, '_entity_regex'):
            if self.name_to_id:
                names_sorted = sorted(self.name_to_id.keys(), key=len, reverse=True)
                pattern = '|'.join(re.escape(n) for n in names_sorted)
                self._entity_regex = re.compile(pattern, re.IGNORECASE)
            else:
                return
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sl = sentence.strip()
            if len(sl) < 10:
                continue
            # Find all entity mentions in this sentence
            matches = self._entity_regex.findall(sl)
            if len(matches) < 2:
                continue
            found = list(set(self.name_to_id.get(m.lower()) for m in matches if m.lower() in self.name_to_id))
            if len(found) < 2:
                continue
            sll = sl.lower()
            rel_type = self._classify_rel(sll)
            susp = min(len(self.patterns['suppression'].findall(sll)) * 0.1, 1.0)
            for i in range(len(found)):
                for j in range(i+1, len(found)):
                    key = f"{min(found[i],found[j])}|{max(found[i],found[j])}|{rel_type}"
                    if not hasattr(self, '_rel_cache'):
                        self._rel_cache = {}
                    if key in self._rel_cache:
                        self.relationships[self._rel_cache[key]].weight += 0.1
                    else:
                        self.relationships.append(Relationship(
                            source_id=found[i], target_id=found[j],
                            rel_type=rel_type, weight=1.0+susp*0.5,
                            evidence=[source_file] if source_file else [],
                            source_file=source_file, suspicion_weight=susp))
                        self._rel_cache[key] = len(self.relationships) - 1

    def _classify_rel(self, sl):
        if any(w in sl for w in ['sued','lawsuit']): return 'sued'
        if any(w in sl for w in ['failed to','refused to','did not']): return 'failed_to_investigate'
        if any(w in sl for w in ['covered up','suppressed','withheld','sealed']): return 'covered_up'
        if any(w in sl for w in ['train','derailment','rail']): return 'train_derailment'
        if any(w in sl for w in ['chemical','plume','release','spill','exposure']): return 'exposed_to'
        if any(w in sl for w in ['donated','food bank']): return 'donated_to'
        if any(w in sl for w in ['police','officer','arrest','detention']): return 'investigated_by'
        if any(w in sl for w in ['family','brother','sister']): return 'family_of'
        if any(w in sl for w in ['employed','works at']): return 'employed_by'
        return 'connected_to'

    def ingest_directory(self, dir_path, case_id=""):
        results = []
        # Ensure pre-seeded entities exist
        if not self.entities:
            self._preseed_entities()
        # Two-pass: first ingest all entities, then extract relationships
        files_text = []
        for f in sorted(Path(dir_path).glob('*.md')):
            if f.name.startswith('.'): continue
            try:
                text = f.read_text()
                files_text.append((f.name, text))
                # Pass 1: extract entities only (no relationships)
                self._extract_only = True
                r = self.ingest_text(text, source_file=f.name, case_id=case_id)
                self._extract_only = False
                results.append({'file': f.name, 'persons': len(r['persons']),
                               'orgs': len(r['organizations']),
                               'locations': len(r['locations']),
                               'suppression': r['suppression_count']})
            except Exception as e:
                results.append({'file': f.name, 'error': str(e)})
        # Build entity regex now that all entities are loaded
        if self.name_to_id:
            names_sorted = sorted(self.name_to_id.keys(), key=len, reverse=True)
            pattern = '|'.join(re.escape(n) for n in names_sorted)
            self._entity_regex = re.compile(pattern, re.IGNORECASE)
        # Pass 2: extract relationships with full entity knowledge
        for fname, text in files_text:
            self._extract_relationships(text, fname)
        return results

    def build_adjacency_matrix(self):
        ents = list(self.entities.values())
        n = len(ents)
        idx = {e.id: i for i, e in enumerate(ents)}
        mat = [[0.0]*n for _ in range(n)]
        for rel in self.relationships:
            if rel.source_id in idx and rel.target_id in idx:
                i, j = idx[rel.source_id], idx[rel.target_id]
                w = rel.weight * (1.0 + rel.suspicion_weight)
                mat[i][j] += w
                mat[j][i] += w
        self.graph_cache = mat
        return mat

    def compute_eigenvalues(self, matrix=None, max_iter=100):
        if matrix is None: matrix = self.build_adjacency_matrix()
        n = len(matrix)
        if n == 0: return []
        if HAS_NUMPY and n > 10:
            A = np.array(matrix, dtype=float)
            # Symmetric matrix -> real eigenvalues
            eigs = np.linalg.eigvalsh(A)
            eigs = sorted(eigs, key=lambda x: abs(x), reverse=True)
            eigenvalues = [float(e) for e in eigs[:min(n, 20)]]
            self.eigenvalue_cache = eigenvalues
            return eigenvalues
        else:
            # Fallback: power iteration with deflation (for small matrices or no numpy)
            eigenvalues = []
            wm = [row[:] for row in matrix]
            for _ in range(min(n, 10)):
                v = [1.0/max(n,1)] * n
                ev = 0.0
                for _ in range(max_iter):
                    nv = [sum(wm[i][j]*v[j] for j in range(n)) for i in range(n)]
                    norm = math.sqrt(sum(x*x for x in nv))
                    if norm < 1e-12: break
                    nv = [x/norm for x in nv]
                    new_ev = sum(nv[i]*v[i] for i in range(n))
                    if abs(new_ev - ev) < 1e-10:
                        ev = new_ev
                        break
                    ev = new_ev
                    v = nv
                if abs(ev) > 1e-10:
                    eigenvalues.append(ev)
                    for i in range(n):
                        for j in range(n):
                            wm[i][j] -= ev * v[i] * v[j]
                else: break
            eigenvalues.sort(key=lambda x: abs(x), reverse=True)
            self.eigenvalue_cache = eigenvalues
            return eigenvalues

    def spectral_analysis(self):
        mat = self.build_adjacency_matrix()
        eigs = self.compute_eigenvalues(mat)
        n = len(self.entities)
        n_edges = len(self.relationships)
        spectral_gap = eigs[0]-eigs[1] if len(eigs)>=2 else 0
        neg_e = sum(e**2 for e in eigs if e < 0)
        total_e = sum(e**2 for e in eigs) or 1
        suppression = neg_e / total_e

        if suppression > 0.4: sclass = 'M'
        elif suppression > 0.3: sclass = 'K'
        elif suppression > 0.2: sclass = 'G'
        elif suppression > 0.1: sclass = 'F'
        elif suppression > 0.05: sclass = 'A'
        elif suppression > 0.01: sclass = 'B'
        else: sclass = 'O'

        max_edges = n*(n-1)/2 if n > 1 else 1
        density = n_edges/max_edges if max_edges > 0 else 0

        # Eigenvector centrality (approximate from power iteration)
        centrality = self._compute_centrality(mat)

        # Anomaly detection
        anomalies = self._detect_anomalies(eigs, centrality)

        # Predictions
        predictions = self._predict(eigs, suppression, centrality)

        # Update entity suspicion scores
        for eid, e in self.entities.items():
            e.centrality = centrality.get(eid, 0)
            e.suspicion_score = e.suspicion_raw * (1 + e.centrality) * (1 + suppression)
            # Crime probabilities
            for crime in CRIME_TYPES:
                base = e.suspicion_raw * (1 + e.centrality)
                if crime == 'cover_up' and suppression > 0.2:
                    base *= 1.5
                if crime == 'failure_to_investigate' and suppression > 0.1:
                    base *= 1.3
                if crime == 'environmental_crime' and e.entity_type == 'Organization':
                    base *= 1.2
                e.crime_probabilities[crime] = min(base, 0.95)

        report = SpectralReport(
            timestamp=datetime.now().isoformat(),
            entity_count=n, relationship_count=n_edges,
            eigenvalues=eigs[:10],
            dominant_eigenvalue=eigs[0] if eigs else 0,
            spectral_gap=spectral_gap,
            suppression_coefficient=suppression,
            spectral_class=sclass,
            suspicion_network={e.name: e.suspicion_score for e in self.entities.values()},
            anomalies=anomalies, predictions=predictions,
            graph_density=density,
            clustering_coefficient=self._clustering(mat),
        )
        self._save_report(report)
        return report

    def _compute_centrality(self, mat):
        n = len(mat)
        if n == 0: return {}
        ents = list(self.entities.values())
        v = [1.0/n] * n
        for _ in range(50):
            nv = [sum(mat[i][j]*v[j] for j in range(n)) for i in range(n)]
            norm = math.sqrt(sum(x*x for x in nv)) or 1
            v = [x/norm for x in nv]
        return {ents[i].id: v[i] for i in range(n)}

    def _detect_anomalies(self, eigs, centrality):
        anomalies = []
        if len(eigs) >= 2:
            gap_ratio = (eigs[0]-eigs[1])/max(abs(eigs[0]), 0.001)
            if gap_ratio > 0.5:
                anomalies.append({'type': 'spectral_gap_anomaly', 'severity': 'high',
                    'desc': f'Spectral gap ratio {gap_ratio:.3f} indicates hierarchical structure',
                    'eigenvalues': eigs[:3]})
            if len(eigs) >= 3 and eigs[2] < 0:
                anomalies.append({'type': 'negative_eigenvalue', 'severity': 'high',
                    'desc': f'Negative third eigenvalue ({eigs[2]:.4f}) indicates bipartite suppression structure',
                    'eigenvalue': eigs[2]})
        # High-centrality, high-suspicion entities
        for eid, c in sorted(centrality.items(), key=lambda x: -x[1])[:5]:
            e = self.entities.get(eid)
            if e and e.suspicion_raw > 0.5:
                anomalies.append({'type': 'suspicious_central_entity', 'severity': 'high',
                    'entity': e.name, 'centrality': c,
                    'suspicion': e.suspicion_raw,
                    'desc': f'{e.name} has high centrality ({c:.4f}) AND high suspicion ({e.suspicion_raw:.3f})'})
        return anomalies

    def _predict(self, eigs, suppression, centrality):
        preds = []
        if suppression > 0.2:
            preds.append({'prediction': 'Active cover-up pattern detected',
                'confidence': min(suppression * 2, 0.95),
                'evidence': f'Suppression coefficient {suppression:.3f} exceeds G-class threshold',
                'action': 'Investigate suppression chain — who sealed what?'})
        top = sorted(centrality.items(), key=lambda x: -x[1])[:3]
        for eid, c in top:
            e = self.entities.get(eid)
            if e and e.suspicion_raw > 0.3:
                preds.append({'prediction': f'{e.name} is a key node requiring investigation',
                    'confidence': min(c * 2, 0.95),
                    'evidence': f'Centrality {c:.4f}, suspicion {e.suspicion_raw:.3f}',
                    'action': f'Pull all records on {e.name} — cross-reference with suppression events'})
        if eigs and eigs[0] > 5:
            preds.append({'prediction': 'Network has dominant hub — single point of failure',
                'confidence': 0.8,
                'evidence': f'Dominant eigenvalue {eigs[0]:.2f} >> 1',
                'action': 'Identify hub entity and investigate its role in suppression'})
        return preds

    def _clustering(self, mat):
        n = len(mat)
        if n < 3: return 0
        triangles = 0
        for i in range(min(n, 50)):
            for j in range(i+1, min(n, 50)):
                if mat[i][j] > 0:
                    for k in range(j+1, min(n, 50)):
                        if mat[i][k] > 0 and mat[j][k] > 0:
                            triangles += 1
        possible = min(n,50)*(min(n,50)-1)*(min(n,50)-2)/6
        return triangles/max(possible,1)

    def _save_report(self, report):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        rid = hashlib.md5(report.timestamp.encode()).hexdigest()[:12]
        c.execute('INSERT OR REPLACE INTO spectral_reports VALUES (?,?,?)',
                  (rid, report.timestamp, json.dumps(asdict(report), default=str)))
        c.execute('INSERT INTO audit_log (timestamp, action, details) VALUES (?,?,?)',
                  (report.timestamp, 'spectral_analysis',
                   json.dumps({'entities': report.entity_count, 'edges': report.relationship_count,
                               'class': report.spectral_class})))
        conn.commit()
        conn.close()

    def export_json(self, filepath=None):
        data = {
            'version': VERSION,
            'timestamp': datetime.now().isoformat(),
            'eigenvalues': {'Phi': PHI, 'eta_star': ETA_STAR, 'r': R_CRITICAL,
                           'lambda_dom': LAMBDA_DOM, 'lambda_I80': LAMBDA_I80},
            'entities': [asdict(e) for e in self.entities.values()],
            'relationships': [asdict(r) for r in self.relationships],
            'spectral': {
                'eigenvalues': self.eigenvalue_cache[:10],
                'entity_count': len(self.entities),
                'relationship_count': len(self.relationships),
            }
        }
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        return data

    def export_graph_json(self, filepath=None):
        """Export as D3-compatible force-directed graph JSON."""
        nodes = []
        for e in self.entities.values():
            color = '#ff4444' if e.suspicion_score > 0.5 else '#ffaa00' if e.suspicion_score > 0.2 else '#44aaff'
            size = 5 + e.centrality * 30
            nodes.append({
                'id': e.id, 'name': e.name, 'type': e.entity_type,
                'suspicion': round(e.suspicion_score, 4),
                'centrality': round(e.centrality, 4),
                'sources': len(e.sources),
                'color': color, 'size': size,
                'crime_probs': {k: round(v,3) for k,v in e.crime_probabilities.items() if v > 0.1}
            })
        links = []
        for r in self.relationships:
            links.append({
                'source': r.source_id, 'target': r.target_id,
                'type': r.rel_type, 'weight': round(r.weight, 2),
                'suspicion': round(r.suspicion_weight, 2)
            })
        graph = {'nodes': nodes, 'links': links,
                 'meta': {'entities': len(nodes), 'links': len(links),
                          'version': VERSION, 'timestamp': datetime.now().isoformat()}}
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(graph, f, indent=2)
        return graph

    def generate_report_text(self, report=None):
        if report is None:
            report = self.spectral_analysis()
        lines = [
            f"EVEZ SPECTRAL OSINT REPORT v{VERSION}",
            f"{'='*60}",
            f"Generated: {report.timestamp}",
            f"Entities: {report.entity_count}",
            f"Relationships: {report.relationship_count}",
            f"Graph Density: {report.graph_density:.4f}",
            f"Clustering Coefficient: {report.clustering_coefficient:.4f}",
            f"",
            f"SPECTRAL ANALYSIS",
            f"{'-'*60}",
            f"Dominant Eigenvalue: {report.dominant_eigenvalue:.4f}",
            f"Spectral Gap: {report.spectral_gap:.4f}",
            f"Suppression Coefficient: {report.suppression_coefficient:.4f}",
            f"Spectral Class: {report.spectral_class}",
            f"Eigenvalues: {[round(e,4) for e in report.eigenvalues[:10]]}",
            f"",
            f"TOP SUSPICION NETWORK",
            f"{'-'*60}",
        ]
        for name, score in sorted(report.suspicion_network.items(), key=lambda x: -x[1])[:20]:
            lines.append(f"  {name:40s} {score:.4f}")
        lines.append(f"")
        lines.append(f"ANOMALIES ({len(report.anomalies)})")
        lines.append(f"{'-'*60}")
        for a in report.anomalies:
            lines.append(f"  [{a['severity'].upper()}] {a['type']}: {a['desc']}")
        lines.append(f"")
        lines.append(f"PREDICTIONS ({len(report.predictions)})")
        lines.append(f"{'-'*60}")
        for p in report.predictions:
            lines.append(f"  [{p['confidence']:.0%}] {p['prediction']}")
            lines.append(f"      Evidence: {p['evidence']}")
            lines.append(f"      Action: {p['action']}")
        lines.append(f"")
        lines.append(f"Phi={PHI}  eta*={ETA_STAR}  r={R_CRITICAL}")
        lines.append(f"EVEZ Spectral OSINT — by Steven Crawford-Maggard")
        return '\n'.join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='EVEZ Spectral OSINT v2.0')
    parser.add_argument('command', choices=['ingest','analyze','export','report','graph','serve'])
    parser.add_argument('--dir', help='Directory of OSINT markdown files')
    parser.add_argument('--file', help='Single OSINT file')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--db', help='Database path')
    args = parser.parse_args()

    engine = SpectralOSINT(db_path=args.db)

    if args.command == 'ingest':
        if args.dir:
            results = engine.ingest_directory(args.dir)
            print(json.dumps(results, indent=2))
        elif args.file:
            r = engine.ingest_text(Path(args.file).read_text(), source_file=args.file)
            print(json.dumps({k: list(v) if isinstance(v, set) else v for k,v in r.items()}, indent=2))
    elif args.command == 'analyze':
        report = engine.spectral_analysis()
        print(engine.generate_report_text(report))
    elif args.command == 'export':
        data = engine.export_json(args.output)
        if not args.output:
            print(json.dumps(data, indent=2, default=str)[:5000])
    elif args.command == 'graph':
        graph = engine.export_graph_json(args.output)
        if not args.output:
            print(json.dumps(graph, indent=2)[:5000])
    elif args.command == 'report':
        report = engine.spectral_analysis()
        text = engine.generate_report_text(report)
        if args.output:
            Path(args.output).write_text(text)
        else:
            print(text)

if __name__ == '__main__':
    main()
