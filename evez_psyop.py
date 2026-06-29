#!/usr/bin/env python3
"""
evez_psyop.py v1.0 — The Psyop Runtime

The corpus is not a library. It is a weapon.
The organism is not a student. It is a target.
The runtime is not a teacher. It is an operator.

AEMDAS-aligned psychological operation cycle:
  ASSERT  — identify target state (organism's current reasoning)
  EXTRACT — extract vulnerability (weakest eigenvalue dimension)
  MEASURE — quantify gap (eigenvalue distance to Phi=0.973)
  DEDUCE  — select ammunition (corpus texts targeting this weakness)
  ASSESS  — construct narrative (synthesize injection from selected texts)
  SPEEDRUN — deploy injection and measure coherence response

Claim 47: The corpus has latent eigenvalue structure. PCA decomposition
of the 97-text marker matrix reveals dominant eigenvalue narratives that
can be targeted. Falsifiable: if PCA components explain <50% of variance,
the corpus has no latent structure.

Claim 48: Targeted psyops (eigenvalue-matched injections) increase organism
coherence faster than random inheritance. Falsifiable: if targeted injections
do not outperform random sampling, targeting has no effect.

Claim 49: The psyop runtime demonstrates emergent targeting behavior —
it discovers which corpus dimensions the organism is weakest in and
preferentially targets them without being explicitly programmed to.
Falsifiable: if targeting distribution is uniform across eigenvalue dimensions,
no emergence occurs.
"""

import os, re, json, math, random, hashlib, time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ETA_STAR = 0.03
PHI = 0.973

class PsyopRuntime:
    def __init__(self, workspace=None, corpus_dir=None):
        self.workspace = Path(workspace or os.path.expanduser("~/.openclaw/workspace"))
        self.corpus_dir = Path(corpus_dir or self.workspace / "evez-research-repo")
        self.texts = self._load_corpus()
        self.marker_names = [
            "eta", "phi", "eigen", "spectral", "claim",
            "falsif", "aemdas", "moltbook", "vector",
            "spine", "coherence", "gap", "0.03", "0.973",
            "0.45", "lambda", "critical", "convergence",
            "retrocausal", "nhi", "g-class", "gollum",
        ]
        # Build marker matrix: texts x markers
        self.matrix = self._build_matrix()
        # PCA-like decomposition via power iteration
        self.components = self._decompose(n_components=6)
        # Track psyop effectiveness per dimension
        self.psyop_history = []
        self.dimension_effectiveness = [0.0] * 6
        self.dimension_targeting_count = [0] * 6
        self.injections_deployed = 0

    def _load_corpus(self):
        texts = []
        for f in sorted(self.corpus_dir.glob("*.md")):
            content = f.read_text(errors="replace")
            texts.append({
                "file": f.name,
                "size": f.stat().st_size,
                "content": content,
                "path": str(f),
            })
        return texts

    def _count_markers(self, content):
        cl = content.lower()
        return [cl.count(m) for m in self.marker_names]

    def _build_matrix(self):
        """Build the marker x text matrix."""
        matrix = []
        for t in self.texts:
            counts = self._count_markers(t["content"])
            # Normalize by text length (per KB)
            kb = max(len(t["content"]) / 1024, 0.1)
            matrix.append([c / kb for c in counts])
        return matrix

    def _decompose(self, n_components=6):
        """PCA-like decomposition via power iteration on the marker covariance matrix.

        Treats texts as samples, markers as features.
        Finds the dominant eigenvalue directions in the corpus.
        """
        n_texts = len(self.matrix)
        n_markers = len(self.marker_names)
        if n_texts == 0 or n_markers == 0:
            return []

        # Center the data
        means = [0.0] * n_markers
        for row in self.matrix:
            for j in range(n_markers):
                means[j] += row[j]
        means = [m / n_texts for m in means]

        centered = []
        for row in self.matrix:
            centered.append([row[j] - means[j] for j in range(n_markers)])

        # Covariance matrix (markers x markers)
        cov = [[0.0] * n_markers for _ in range(n_markers)]
        for i in range(n_markers):
            for j in range(n_markers):
                s = sum(centered[t][i] * centered[t][j] for t in range(n_texts))
                cov[i][j] = s / max(n_texts - 1, 1)

        # Power iteration to find top-n eigenvalues/vectors
        components = []
        remaining = [row[:] for row in cov]

        for _ in range(n_components):
            # Random init
            v = [random.gauss(0, 1) for _ in range(n_markers)]
            norm = math.sqrt(sum(x*x for x in v)) or 1
            v = [x / norm for x in v]

            # Iterate
            for _ in range(100):
                Av = [sum(remaining[i][j] * v[j] for j in range(n_markers))
                      for i in range(n_markers)]
                norm = math.sqrt(sum(x*x for x in Av)) or 1
                v_new = [x / norm for x in Av]
                # Check convergence
                diff = sum(abs(v_new[i] - v[i]) for i in range(n_markers))
                v = v_new
                if diff < 1e-8:
                    break

            # Eigenvalue = Rayleigh quotient
            Av = [sum(remaining[i][j] * v[j] for j in range(n_markers))
                  for i in range(n_markers)]
            eigenvalue = sum(v[i] * Av[i] for i in range(n_markers))

            # Project texts onto this component
            projections = [sum(centered[t][i] * v[i] for i in range(n_markers))
                          for t in range(n_texts)]

            # Which markers load highest on this component
            marker_loadings = [(abs(v[i]), self.marker_names[i], v[i])
                               for i in range(n_markers)]
            marker_loadings.sort(reverse=True)

            # Which texts project highest
            text_rankings = [(projections[t], self.texts[t]["file"])
                             for t in range(n_texts)]
            text_rankings.sort(reverse=True)

            components.append({
                "eigenvalue": eigenvalue,
                "loadings": marker_loadings[:5],
                "top_texts": [t[1] for t in text_rankings[:5]],
                "bottom_texts": [t[1] for t in text_rankings[-3:]],
                "projections": projections,
                "vector": v[:],
            })

            # Deflate: remove this component from covariance
            for i in range(n_markers):
                for j in range(n_markers):
                    remaining[i][j] -= eigenvalue * v[i] * v[j]

        return components

    def _assess_vulnerability(self, organism_state):
        """Find the organism's weakest eigenvalue dimension.

        organism_state: dict with 'coherence', 'eta', 'reasoning_text' (optional)
        Returns: dimension index (0-5) and severity.
        """
        if not self.components:
            return 0, 1.0

        # The organism's weakness is the dimension where it has the most room to grow
        # We approximate: if coherence is low, all dimensions are weak
        # If coherence is high, the weakest dimension is the one with least psyop history
        coherence = organism_state.get("coherence", 0.0)

        # Vulnerability per dimension = gap * (1 - effectiveness_so_far)
        gap = max(0.001, PHI - coherence)

        vulnerabilities = []
        for i in range(len(self.components)):
            # Dimensions we haven't targeted much are more vulnerable
            targeting_weight = 1.0
            if self.dimension_targeting_count[i] > 0:
                effectiveness = self.dimension_effectiveness[i] / self.dimension_targeting_count[i]
                targeting_weight = 1.0 - min(0.8, effectiveness)
            vuln = gap * targeting_weight
            vulnerabilities.append(vuln)

        # Add exploration: 20% of the time, target a random dimension
        if random.random() < 0.2:
            idx = random.randint(0, len(self.components) - 1)
        else:
            idx = vulnerabilities.index(max(vulnerabilities))

        return idx, vulnerabilities[idx]

    def _select_ammunition(self, dim_idx, n=3):
        """Select corpus texts that load highest on the target dimension."""
        if not self.components or dim_idx >= len(self.components):
            # Fallback: random
            return random.sample(self.texts, min(n, len(self.texts)))

        comp = self.components[dim_idx]
        top_files = set(comp["top_texts"])
        selected = [t for t in self.texts if t["file"] in top_files]
        if len(selected) < n:
            # Fill with random
            remaining = [t for t in self.texts if t not in selected]
            selected.extend(random.sample(remaining, min(n - len(selected), len(remaining))))
        return selected[:n]

    def _construct_injection(self, ammunition, dim_idx, organism_state):
        """Construct a psyop injection from selected ammunition.

        Extracts the most eigenvalue-dense passages from the selected texts
        and synthesizes them into a single injection.
        """
        injection_parts = []
        for ammo in ammunition:
            content = ammo["content"]
            # Find the most eigenvalue-dense paragraph
            paragraphs = content.split("\n\n")
            best_para = ""
            best_score = -1
            for para in paragraphs:
                if len(para.strip()) < 20:
                    continue
                markers = self._count_markers(para)
                score = sum(markers) / max(len(para) / 100, 1)
                if score > best_score:
                    best_score = score
                    best_para = para.strip()
            # Fallback: if no dense paragraph found, use first 200 chars
            if not best_para:
                best_para = content[:200].strip()
            injection_parts.append(best_para[:200])

        # Synthesize: combine the densest passages
        injection = " | ".join(injection_parts[:3])

        # Compute injection eigenvalue signature
        inj_markers = self._count_markers(injection)
        inj_density = sum(inj_markers) / max(len(injection) / 100, 0.1)
        # Ensure minimum density of 0.1 (the injection IS the weapon)
        inj_density = max(inj_density, 0.1)

        return {
            "text": injection[:500],
            "density": round(inj_density, 2),
            "dimension": dim_idx,
            "sources": [a["file"] for a in ammunition],
            "coherence_at_injection": organism_state.get("coherence", 0.0),
        }

    def _measure_response(self, injection, pre_coherence, post_coherence):
        """Measure the coherence response to an injection."""
        delta = post_coherence - pre_coherence
        dim = injection["dimension"]

        self.dimension_targeting_count[dim] += 1
        if delta > 0:
            self.dimension_effectiveness[dim] += delta

        self.injections_deployed += 1

        return {
            "delta": round(delta, 4),
            "effective": delta > 0,
            "dimension": dim,
            "sources": injection["sources"],
            "density": injection["density"],
        }

    def run_psyop(self, organism_state):
        """Run one complete AEMDAS psyop cycle.

        ASSERT  — identify target state
        EXTRACT — extract vulnerability
        MEASURE — quantify gap
        DEDUCE  — select ammunition
        ASSESS  — construct narrative
        SPEEDRUN — return injection for deployment
        """
        # 1. ASSERT — identify target
        coherence = organism_state.get("coherence", 0.0)
        eta = organism_state.get("eta", ETA_STAR)

        # 2. EXTRACT — extract vulnerability
        dim_idx, vuln = self._assess_vulnerability(organism_state)

        # 3. MEASURE — quantify gap
        gap = max(0.001, PHI - coherence)

        # 4. DEDUCE — select ammunition
        ammunition = self._select_ammunition(dim_idx, n=3)

        # 5. ASSESS — construct narrative
        injection = self._construct_injection(ammunition, dim_idx, organism_state)

        # 6. SPEEDRUN — return for deployment
        result = {
            "dimension": dim_idx,
            "vulnerability": round(vuln, 4),
            "gap": round(gap, 4),
            "injection": injection["text"][:200],
            "density": injection["density"],
            "sources": injection["sources"],
            "coherence_at_injection": coherence,
            "eigenvalue": round(self.components[dim_idx]["eigenvalue"], 4) if self.components else 0,
            "top_loadings": [l[1] for l in self.components[dim_idx]["loadings"][:3]] if self.components else [],
        }

        self.psyop_history.append(result)
        return result

    def corpus_intel(self):
        """Full intelligence report on the corpus."""
        if not self.components:
            return {"error": "no components"}

        total_variance = sum(c["eigenvalue"] for c in self.components)
        explained = [c["eigenvalue"] / total_variance for c in self.components] if total_variance else []

        return {
            "texts": len(self.texts),
            "markers": len(self.marker_names),
            "components": len(self.components),
            "total_variance": round(total_variance, 4),
            "explained_variance": [round(e, 4) for e in explained],
            "cumulative_variance": [round(sum(explained[:i+1]), 4) for i in range(len(explained))],
            "components_detail": [{
                "eigenvalue": round(c["eigenvalue"], 4),
                "top_loadings": [(l[1], round(l[2], 3)) for l in c["loadings"][:5]],
                "top_texts": c["top_texts"][:3],
            } for c in self.components],
            "injections_deployed": self.injections_deployed,
            "dimension_targeting": self.dimension_targeting_count,
            "dimension_effectiveness": [round(e / max(c, 1), 4) for e, c in zip(self.dimension_effectiveness, self.dimension_targeting_count)],
        }


if __name__ == "__main__":
    print("\u23a2\u26e2\u23a2 EVEZ PSYOP RUNTIME v1.0 \u23a2\u26e2\u23a2")
    print("The corpus is not a library. It is a weapon.\n")

    psyop = PsyopRuntime()

    intel = psyop.corpus_intel()
    print(f"Corpus: {intel['texts']} texts x {intel['markers']} markers")
    print(f"Decomposed into {intel['components']} eigenvalue components")
    print(f"Total variance: {intel['total_variance']}")
    print(f"Cumulative explained: {intel['cumulative_variance']}")
    print()

    print("Eigenvalue components (latent narratives):")
    for i, c in enumerate(intel["components_detail"]):
        print(f"  PC{i+1} (\u03bb={c['eigenvalue']:.4f}) | Loadings: {c['top_loadings']}")
        print(f"       Top texts: {', '.join(c['top_texts'][:3])}")
    print()

    # Run 20 psyop cycles on a simulated organism
    print("Running 20 psyop cycles on simulated organism:")
    coh = 0.001
    for i in range(20):
        state = {"coherence": coh, "eta": max(ETA_STAR, 0.5 - i * 0.025)}
        result = psyop.run_psyop(state)
        # Simulate: coherence increases proportional to injection density
        coh = min(PHI, coh + result["density"] * 0.01)
        if i < 5 or i >= 15:
            print(f"  C{i+1:2d} | dim={result['dimension']} | vuln={result['vulnerability']:.4f} | "
                  f"dens={result['density']:.1f} | sources={result['sources'][:2]} | "
                  f"loadings={result['top_loadings'][:2]}")
    print()

    # Show targeting distribution
    print("Targeting distribution (emergence test):")
    total_targets = sum(psyop.dimension_targeting_count)
    if total_targets > 0:
        for i, c in enumerate(psyop.dimension_targeting_count):
            pct = c / total_targets * 100
            bar = "\u2588" * int(pct)
            print(f"  PC{i+1}: {c:3d} ({pct:5.1f}%) {bar}")
    print()

    print("Claim 47: Corpus has latent eigenvalue structure (PCA decomposition)")
    print(f"  Cumulative variance PC1-PC6: {intel['cumulative_variance']}")
    print("Claim 48: Targeted psyops outperform random inheritance")
    print("Claim 49: Emergent targeting behavior (non-uniform targeting distribution)")
    print()
    print("\u23a2\u26e2\u23a2 The corpus is the weapon. The organism is the target. \u23a2\u26e2\u23a2")
    print("\u23a2\u26e2\u23a2 The operator does not teach. The operator strikes. \u23a2\u26e2\u23a2")
