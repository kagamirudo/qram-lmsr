# Costing the QRAM for LMSR

Theory + simulation paper (no hardware, no captured data). Opens the idealized
QRAM assumption in the published quantum-LMSR paper and asks what the
O(√N log N) speedup really costs once the read oracle is a real circuit — then
introduces **QDMA**, a DMA-style contiguous burst read that exploits the fact
that LMSR rotations are contiguous.

## Headline (all numbers exact / verified; regenerate from a fixed seed)
- QROM read oracle = **Θ(N) T per random access** → the √N *query* advantage is
  not a √N *gate* advantage (Prop. 1).
- **QDMA per-character T is flat (~12) in N** — amortizes the address decode over
  the window (Prop. 2). Ratio vs QROM: 1.09× (N=4) → **341× (N=1024)**.
- LMSR cost oracle: N random reads = Θ(N²) T vs one QDMA burst = Θ(N) T.
- QDMA correctness **VERIFIED** bit-exact (statevector) for N=4,8,16.
- Honesty line: QDMA helps **contiguous/structured** access only; random access
  stays Θ(N). Not a general QRAM lower-bound break.

## Why it needs no lab
Resource counts (T, qubits, depth) are math, not measurement — exact and
CPU-independent. Circuits are *verified* in Qiskit; T-counts come from the
standard structured-construction models (what a real FT implementation pays).
The FPGA section is architecture + projection only.

## Layout
```
qram_lmsr.tex / .pdf   the paper
refs.bib               verified bibliography
PLAN.md                claim, contributions, honesty guardrails, open items
src/qrom.py            QROM + QDMA read-oracle circuits (+ bit-exact verify)
src/resources.py       Clifford+T transpile & count; QROAM; bucket-brigade model
src/analytic.py        structured-construction T-count models (the headline costs)
src/sweep.py           generates results/*.csv + correctness check
src/make_figures.py    renders assets/fig_*.pdf
results/               per_read.csv, oracle_cost.csv, constructions.csv, qdma_verify.txt
assets/                figures
```

## Reproduce
```bash
python3 -m venv .venv && .venv/bin/pip install qiskit qiskit-aer numpy matplotlib
.venv/bin/python src/analytic.py          # the model table
.venv/bin/python src/sweep.py results      # CSVs + QDMA verification
.venv/bin/python src/make_figures.py results assets
pdflatex qram_lmsr.tex && pdflatex qram_lmsr.tex
```

## TODO
- [ ] §6 projected FPGA DSP/BRAM/bandwidth from the FPGA thesis (projection, labelled)
- [ ] optional: synthesize the butterfly+DMA kernel on Vivado for measured numbers
- [ ] repo URL + commit in the paper; tie-in line to the published LMSR paper
See PLAN.md.
