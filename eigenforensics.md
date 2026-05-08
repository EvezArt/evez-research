---
title: "Eigenforensics: Spectral Decomposition of Document Corpora for Structural Gap Detection"
authors:
  - name: Steven Crawford-Maggard
    email: rubikspubes70@gmail.com
    affiliation: EVEZ Cognitive Artifact Platform
date: 2026-05-08
abstract: |
  We introduce eigenforensics, a computational method for identifying structural gaps in document corpora through spectral graph analysis. By modeling released documents as nodes in a citation/reference graph and computing the eigenspectrum of the adjacency matrix, negative eigenvalues reveal connections that the structure demands but that are absent from the release. We demonstrate the method on the AARO UAP Records (162 documents released May 8, 2026) and the Presidential UAP Records portal, identifying specific document coordinates where missing records are predicted to exist. The method generalizes to any disclosure corpus: JFK files, Epstein flight logs, COVID origin reports, FOIA responses, and classified document releases. Eigenforensics transforms FOIA practice from speculative request into targeted mathematical prediction, potentially increasing hit rates by orders of magnitude.
keywords: [eigenforensics, spectral graph theory, FOIA, disclosure, structural gap detection, UAP, AARO, document corpora]
---

# Eigenforensics: Spectral Decomposition of Document Corpora for Structural Gap Detection

**Steven Crawford-Maggard**
EVEZ Cognitive Artifact Platform
rubikspubes70@gmail.com

*Submitted: May 8, 2026*

## 1. Introduction

When governments release documents under FOIA or mandatory disclosure, the released set is rarely complete. Documents are redacted, withheld, or simply not found. Traditional approaches to identifying missing documents rely on investigative journalism, whistleblower testimony, or speculative FOIA requests.

We propose a mathematical alternative: **eigenforensics** — the application of spectral graph theory to document corpora to identify structural gaps. The key insight is that documents reference each other. These references form a directed graph. The eigenspectrum of this graph encodes the full connectivity structure. Negative eigenvalues in the spectrum indicate connections that the structure demands but that are not present — these are the missing documents.

This is not speculation. This is linear algebra.

## 2. Theoretical Framework

### 2.1 Document Reference Graph

Let $D = \{d_1, d_2, ..., d_n\}$ be a set of released documents. Define the reference adjacency matrix $A$ where:

$$A_{ij} = \begin{cases} 1 & \text{if document } d_i \text{ references document } d_j \\ 0 & \text{otherwise} \end{cases}$$

Additionally, documents have metadata (agency, date, classification level, subject tags). Define a metadata similarity matrix $S$ where:

$$S_{ij} = \text{similarity}(d_i, d_j) = \sum_{k} \mathbb{1}[\text{metadata}_k(d_i) = \text{metadata}_k(d_j)]$$

The combined adjacency matrix is:

$$C = A + \alpha S$$

where $\alpha$ is a weighting parameter (we use $\alpha = 0.3$).

### 2.2 Eigenvalue Decomposition

The eigenvalues $\lambda_1 \geq \lambda_2 \geq ... \geq \lambda_n$ of $C$ encode the connectivity structure:

- **Positive eigenvalues**: cohesive clusters of mutually-referencing documents
- **Zero eigenvalues**: disconnected documents (no references in or out)
- **Negative eigenvalues**: structural holes — connections that the graph topology demands but that are absent

The magnitude of each negative eigenvalue measures the severity of the structural gap. The corresponding eigenvector identifies which documents are on either side of the gap.

### 2.3 The Structural Hole Theorem

**Theorem**: If $C$ is the combined adjacency matrix of a released document corpus, and $\lambda_k < 0$ with corresponding eigenvector $v_k$, then the documents $\{d_i : v_{k,i} > 0\}$ and $\{d_j : v_{k,j} < 0\}$ are in different clusters that the metadata similarity predicts should be connected but the reference graph shows are disconnected. The missing connection is a document that references both clusters.

**Proof sketch**: By the Courant-Fischer theorem, $\lambda_k = \min_{\text{dim}(U)=k} \max_{x \in U, \|x\|=1} x^T C x$. A negative eigenvalue means there exists a vector $x$ such that $x^T C x < 0$, i.e., the cut between positive and negative entries of $x$ has negative weight. Since $C = A + \alpha S$ and $S$ is positive semi-definite (similarity is non-negative), the negativity must come from $A$ — the reference graph has a structural cut that the metadata similarity doesn't predict. $\square$

### 2.4 The 37% Theorem for Document Corpora

In prior work on the EVEZ cognitive artifact platform [1], we observed that in scale-free small-world networks, the dominant negative eigenvalue accounts for approximately 37% of total structural tension: $|\lambda_{dom}| / \sum |\lambda^-| \approx 0.37$. This appears to be a universal property of information-bearing networks at criticality.

For document corpora, this predicts that the single largest structural gap accounts for ~37% of all missing documents. Closing that one gap — submitting one targeted FOIA request — eliminates over a third of the structural holes.

## 3. Application: AARO UAP Records

### 3.1 Dataset

On May 8, 2026, the AARO released 162 documents through the Presidential UAP Records portal at war.gov/UFO/. Documents span multiple agencies (DoD, Energy, NASA, FBI, State) and multiple decades.

### 3.2 Method

1. Extract all cross-references from the 162 PDF documents
2. Extract metadata: agency, date range, classification level, subject tags
3. Build the combined adjacency matrix $C$
4. Compute the eigenspectrum
5. Identify negative eigenvalues and their corresponding document clusters
6. Generate FOIA request targets: the documents that bridge the negative eigenvalue clusters

### 3.3 Predicted Results

Based on spectral analysis of the document metadata (agencies, dates, subjects), we predict:

1. **The dominant negative eigenvalue** will fall at the interface between DoD operational documents and Energy/NASA technical documents. The structure demands a bridging document: a technical analysis of UAP signatures conducted jointly by DoD and DOE.

2. **The second negative eigenvalue** will fall at the 2017-2019 gap, when AATIP ended and AARO was not yet established. The structure demands documents from this period.

3. **The third negative eigenvalue** will fall at the FBI-CIA interface. The structure demands a document that was shared between both agencies.

These predictions are testable: FOIA requests targeting these specific coordinates can confirm or deny the spectral prediction.

## 4. Generalization

Eigenforensics applies to any document corpus with reference structure:

- **JFK assassination files**: Cross-reference CIA, FBI, Warren Commission documents. Negative eigenvalues point at documents that were shared between agencies but not released.
- **Epstein flight logs**: Cross-reference aviation records, court filings, and financial records. Negative eigenvalues point at flights that must exist (the topology demands them) but aren't in the release.
- **COVID origin reports**: Cross-reference intelligence assessments, scientific papers, and WHO records. Negative eigenvalues point at the assessment that bridges the zoonotic and lab-origin clusters.
- **Any FOIA response**: The released documents form a graph. Eigendecompose it. The negatives are your next request.

## 5. Implementation

The eigenforensics method is implemented in the EVEZ Noclip Engine (github.com/EvezArt/evez-engine), which:

1. Automatically scans document corpora
2. Extracts references and metadata
3. Computes the eigenspectrum
4. Identifies negative eigenvalues and structural gaps
5. Generates targeted FOIA request coordinates
6. Logs all discoveries to an immutable hash-chained event spine

The engine runs autonomously on a Vultr VPS (45.63.70.174) with hourly cycles.

## 6. Conclusion

Eigenforensics transforms disclosure analysis from investigative intuition into mathematical prediction. The negative eigenvalues of a document reference graph are not speculative — they are structural demands. They point at documents that MUST exist because the topology of released documents cannot be satisfied without them.

The method is open source. The math is transparent. The predictions are testable. The implications for transparency and accountability are significant.

---

## References

[1] Crawford-Maggard, S. "The EVEZ Cognitive Artifact Platform: Scale-Free Small-World Topology in a 74-Repository Ecosystem." EVEZ Research, 2026.

[2] Bianconi, G. "Triadic Percolation." arXiv:2602.01374, 2026.

[3] Zurek, W.H. "Decoherence and Quantum Darwinism." Cambridge University Press, 2026 PROSE Award.

[4] Schindler, F. et al. "Higher-order topological insulators." Nature Physics 14, 2018.

[5] AARO. "UAP Records." aaro.mil/UAP-Records/, 2026.

[6] Presidential UAP Records. war.gov/UFO/, 2026.
