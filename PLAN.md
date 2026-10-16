# Costing the QRAM for LMSR — paper plan

Status: **theory + simulation paper, full draft with real data** (2026-10-16).
No hardware, no captured data, no benchmark rig — everything is a proof, an exact
circuit resource count, or a clearly-labelled analytic/projected model. Purpose:
thicken the research portfolio and extend the published LMSR paper.

## One-sentence claim
> The O(√N log N) advantage of the quantum LMSR algorithm rests on an idealized
> QRAM whose read oracle, costed at the fault-tolerant circuit level, is itself
> O(N) in T-count per random access; but because LMSR rotations are *contiguous*,
> a DMA-style burst read (QDMA) amortizes the O(N) address decode across the
> window, cutting per-read T to a constant and recovering an N× factor in the
> cost oracle for the structured access pattern LMSR actually uses.

## Why this is honest without a lab
- **Resource counts are math, not measurement.** T-count / qubit / depth of a
  circuit are exact and CPU-independent. Reported from the analytic
  structured-construction model (what a real FT implementation pays), with Qiskit
  used to VERIFY the constructions are correct (not to source T via generic MCX).
- **Correctness is simulatable.** QROM and QDMA verified bit-exact on small N
  (statevector). QDMA burst verified = all addresses load the right word.
- **FPGA stays architecture + projection.** We describe the state-vector
  simulator + DMA memory system and PROJECT resource use; no synthesis claims.
  (The one experimentally-checkable board claim is left for future work.)

## Headline results (results/, all regenerate from a fixed seed)
- QROM per-read T = 4(N-1): 12 (N=4) -> 4092 (N=1024). Linear in N.
- QDMA per-read T -> b*c_write = 12, FLAT in N (amortization).
- Ratio QROM/QDMA per read: 1.09x (N=4) -> 341x (N=1024).
- LMSR cost-oracle speedup (N random decodes vs 1 burst): same 341x at N=1024.
- Construction survey: QROM 4(N-1) T, QROAM ~O(sqrt(Nb)) T, bucket-brigade
  O(N) FT T but only O(log N) active 2q/query (4->20 over N=4..1024).
- QDMA correctness: VERIFIED on N=4,8,16 with random words.

## Contributions
1. Open the LMSR paper's idealized QRAM: show the read oracle is O(N) T per
   random access in a fault-tolerant circuit (the hidden cost of the √N claim).
2. A survey of read-oracle constructions (QROM / QROAM / bucket-brigade)
   costed uniformly for the small-alphabet LMSR word (b=2 bits).
3. QDMA: a descriptor-driven contiguous burst read exploiting LMSR's rotation
   structure; per-read T amortizes to O(1); N× in the cost oracle. Framed as a
   STRUCTURED-ACCESS specialization, NOT a general QRAM lower-bound break.
4. The DMA parallel at two levels: the QDMA oracle, and an FPGA state-vector
   simulator whose own DMA/HBM memory system makes the contiguous-vs-random
   bandwidth argument physically concrete (architecture + projection).

## Honesty guardrails (do not cross)
- QDMA wins ONLY for contiguous/structured reads. Random access stays O(N). Say
  so explicitly and repeatedly.
- Bucket-brigade T is an analytic MODEL from the literature, labelled as such.
- FPGA numbers are PROJECTIONS from the thesis's known utilization, never
  synthesized measurements, unless/until actually run on Vivado.
- No claim that a physical QRAM device works.

## OPEN ITEMS
1. (optional) actually synthesize the FPGA butterfly+DMA kernel on Vivado for a
   MEASURED utilization/timing table — §6 is currently a grounded PROJECTION
   (XC7K325T, 100 MHz, 18-bit Q1.16, AXI-DMA — all real device params from the
   FPGA thesis). Projection is clearly labelled; no red marks remain.
2. Decide venue (arXiv-first like the cube/LMSR line).
3. Verify flagged bib choices (Low 2018-vs-2024, Hann title singular) before any
   submission — already applied the agent's recommendations.

Note (2026-10-16): all red \TODO/\BENCH marks REMOVED; paper is clean for a
professor to read. §6 FPGA projection filled from the real XC7K325T thesis
platform. The ESP32 ROI paper is intentionally left as a pre-paper (keeps its
red board-data placeholders) and is NOT for professor viewing yet.
